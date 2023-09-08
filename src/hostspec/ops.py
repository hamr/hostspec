from collections import defaultdict

# import copy
from dataclasses import dataclass, field
from typing import Iterable, List, Tuple

from .platform import (
    CPUAllocationStrategies,
    HypervisorSpec,
    VirtualSpec,
)


@dataclass
class AllocationData:
    h_spec: HypervisorSpec
    g_specs: Iterable[VirtualSpec]
    # the following derive from h_spec and g_specs
    available_by_node: List[List[int]] = field(init=False)
    numa_nodes_count: int = field(init=False)
    requested_counts: List[int] = field(init=False)

    def __post_init__(self):
        self.available_by_node = self._get_available_by_node()
        self.numa_nodes_count = self._get_numa_nodes_count()
        self.requested_counts = self._get_requested_counts()

    def _get_available_by_node(self) -> List[List[int]]:
        """Return a copy of hypervisor's numa_map with reserved cores removed."""
        if self.h_spec.cpus.numa_map is None:
            raise Exception(f"Not found:  numa_map for {self}")
        reserved_count = self.h_spec.cpus.reserved_cores_per_node
        return [n[reserved_count:] for n in self.h_spec.cpus.numa_map]

    def _get_numa_nodes_count(self) -> int:
        """Return number of numa nodes in self.available_by_node"""
        return len(self.available_by_node)

    def _get_requested_counts(self) -> List[int]:
        """Return list of required cpu counts in g_specs"""
        return [spec.cpus.cpu_count for spec in self.g_specs]

    def _check_requested_cpu_count(self):
        requested_count = sum(self.requested_counts)
        available_count = sum([len(avail) for avail in self.available_by_node])
        if requested_count > available_count:
            raise Exception(
                f"Insufficient available cores for requested allocation: {requested_count} > {self.available_count}"
            )

    def check(self):
        self._check_requested_cpu_count()


@dataclass
class GreedyAllocationData(AllocationData):
    def allocate(self) -> List[Tuple[int, ...]]:
        cpus = list()
        for g_spec in self.g_specs:
            requested = g_spec.cpus.cpu_count
            assigned = self.assign(requested)
            cpus.append(assigned)
        return cpus

    def assign(self, requested) -> Tuple[int, ...]:
        assigned = list()
        for node, cpus in enumerate(self.available_by_node):
            cpus_count = len(cpus)
            # Continue if no cores available on this numa node.
            if cpus_count == 0:
                continue
            # If fewer cores are available than requested, take all of them and
            # continue.
            if cpus_count < requested:
                assigned.extend(cpus)
                self.available_by_node[node] = list()
                requested -= cpus_count
                continue
            # Otherwise, take the requested slice.
            slice = cpus[:requested]
            assigned.extend(slice)
            self.available_by_node[node] = cpus[requested:]
            requested -= len(slice)
        return tuple(assigned)


@dataclass
class PoliteAllocationData(AllocationData):
    def _check_requested_numa_placement(self):
        requested_by_node = defaultdict(list)
        for n, count in enumerate(self.requested_counts):
            node = n % self.numa_nodes_count
            requested_by_node[node].append(count)
        is_gt_available = [
            (node, counts)
            for node, counts in requested_by_node.items()
            if sum(counts) > len(self.available_by_node[node])
        ]
        if is_gt_available:
            raise Exception(
                f"Insufficient available cores to accomodate placement on NUMA nodes ({is_gt_available})"
            )

    def allocate(self) -> List[Tuple[int, ...]]:
        cpus = list()
        for n, g_spec in enumerate(self.g_specs):
            requested = g_spec.cpus.cpu.cores * g_spec.cpus.cpu_count
            # round-robin allocate per numa node
            assigned = self.assign(requested, n % self.numa_nodes_count)
            cpus.append(assigned)
        return cpus

    def assign(self, requested: int, numa_node: int) -> Tuple[int, ...]:
        assigned = self.available_by_node[numa_node][:requested]
        self.available_by_node[numa_node] = self.available_by_node[numa_node][
            requested:
        ]
        return tuple(assigned)

    def check(self):
        super().check()
        self._check_requested_numa_placement()


def assign_cpus(
    h_spec: HypervisorSpec, g_specs: Iterable[VirtualSpec]
) -> Tuple[Tuple[int, ...], ...]:
    """Return a tuple of cpu allocations for each g_spec using the specified cpu
    allocation strategies.

    Handle each strategy separately and put them in the expected order at the
    end.

    Note that the allocation methods modify the allocation data so they need
    their own copy.  Each strategy is safe to process concurrently.
    """
    # polite
    polite_specs = [
        spec
        for spec in g_specs
        if spec.cpus.allocation_strategy == CPUAllocationStrategies.polite
    ]
    polite_allocation_data = PoliteAllocationData(h_spec=h_spec, g_specs=polite_specs)
    polite_allocation_data.check()
    polite_allocations = polite_allocation_data.allocate()

    # greedy
    greedy_specs = [
        spec
        for spec in g_specs
        if spec.cpus.allocation_strategy == CPUAllocationStrategies.greedy
    ]
    greedy_allocation_data = GreedyAllocationData(h_spec=h_spec, g_specs=greedy_specs)
    greedy_allocation_data.check()
    greedy_allocations = greedy_allocation_data.allocate()

    # return the list of allocations in the same order as g_specs
    allocations = list()
    for g_spec in g_specs:
        alloc_strategy = g_spec.cpus.allocation_strategy
        if alloc_strategy == CPUAllocationStrategies.polite:
            allocations.append(polite_allocations.pop(0))
        elif alloc_strategy == CPUAllocationStrategies.greedy:
            allocations.append(greedy_allocations.pop(0))

    return tuple(allocations)
