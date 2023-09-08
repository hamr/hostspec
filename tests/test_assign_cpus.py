# from __future__ import annotations

from typing import Iterable
import itertools

import pytest

from hostspec.defaults import get_host_spec
from hostspec.ops import assign_cpus

# Expected allocations based on what we know about the hypervisor and the
# requested cores.
ALLOCATIONS_TARGETS = {
    # one greedy compute node, 1 core/node reserved for hypervisor
    "c_2023_1": (
        tuple(itertools.chain(range(1, 64), range(65, 128))),
    ),
    # two 20-core workstations, 1 core/node reserved for hypervisor
    "g_2023_1,g_2023_1": (
        tuple(range(1, 21)),   # g_2023_1 @0
        tuple(range(65, 85)),  # g_2023_1 @1
    ),
    # four 20-core workstations, 1 core/node reserved for hypervisor
    "g_2023_1,g_2023_1,g_2023_1,g_2023_1": (
        tuple(range(1, 21)),   # g_2023_1 @0
        tuple(range(65, 85)),  # g_2023_1 @1
        tuple(range(21, 41)),  # g_2023_1 @2
        tuple(range(85, 105)),  # g_2023_1 @3
    ),
    # two 20-core workstations, one greedy compute node, 1 core/node reserved
    # for the hypervisor
    "g_2023_1,g_2023_1,c_2023_1": (
        tuple(range(1, 21)),   # g_2023_1 @0
        tuple(range(65, 85)),  # g_2023_1 @1
        tuple(itertools.chain(range(1, 64), range(65, 128))),  # c_2023_1
    ),
}


@pytest.mark.parametrize(
    "hypervisor_spec_name,guest_spec_names,allocations_target",
    (
        # greedy allocation
        (
            "sm_2023_1_hypervisor",
            ("c_2023_1",),
            ALLOCATIONS_TARGETS["c_2023_1"],
        ),
        # polite allocation
        (
            "sm_2023_1_hypervisor",
            ("g_2023_1", "g_2023_1"),
            ALLOCATIONS_TARGETS["g_2023_1,g_2023_1"],
        ),
        # polite allocation
        (
            "sm_2023_1_hypervisor",
            ("g_2023_1", "g_2023_1", "g_2023_1", "g_2023_1"),
            ALLOCATIONS_TARGETS["g_2023_1,g_2023_1,g_2023_1,g_2023_1"],
        ),
        # combined polite and greedy allocations
        (
            "sm_2023_1_hypervisor",
            ("g_2023_1", "g_2023_1", "c_2023_1"),
            ALLOCATIONS_TARGETS["g_2023_1,g_2023_1,c_2023_1"],
        ),
    )
)
def test_allocate_cpus(
    hypervisor_spec_name: str,
    guest_spec_names: Iterable[str],
    allocations_target: Iterable[Iterable[int]],
):
    h_spec = get_host_spec(hypervisor_spec_name)
    g_specs = [get_host_spec(name) for name in guest_spec_names]
    allocations = assign_cpus(h_spec, g_specs)
    assert allocations == allocations_target
