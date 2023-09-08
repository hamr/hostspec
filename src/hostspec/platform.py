from dataclasses import dataclass
from enum import Enum

from .base import CPUSSpec, HostSpec


class CPUAllocationStrategies(Enum):
    # Polite allocations are discrete sets of vcpus pinned to host cpus,
    # typically confined to a single NUMA node.
    polite = 1
    # Greedy allocations are discrete sets of vcpus pinned to host cpus which
    # may have already been allocated politely.
    greedy = 2
    # Egregious allocations pin vcpus to cpus without regart to other vcpu pins.
    egregious = 3
    # Sneaky allocations use floating (unpinned) cores
    sneaky = 4


# subclasses of classes in base

@dataclass
class HypervisorCPUSSpec(CPUSSpec):
    reserved_cores_per_node: int = 1


@dataclass
class HypervisorSpec(HostSpec):
    cpus: HypervisorCPUSSpec


@dataclass
class VirtualCPUSSpec(CPUSSpec):
    allocation_strategy: CPUAllocationStrategies = CPUAllocationStrategies.polite


@dataclass
class VirtualSpec(HostSpec):
    cpus: VirtualCPUSSpec
