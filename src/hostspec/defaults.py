from .base import (
    CPU,
    CPUSSpec,
    ConfigSpec,
)

from .platform import (
    HypervisorCPUSSpec,
    HypervisorSpec,
    VirtualCPUSSpec,
    VirtualSpec,
    CPUAllocationStrategies,
)


CPUS = {
    "amd1": CPU(name="AMD1", cores=128),
}


CPUS_SPECS = {
    "amd1": CPUSSpec(
        cpu=CPUS["amd1"],
        cpu_count=2,
        threading_enabled=True,
        numa_map=[list(range(64)), list(range(64, 128))],
    ),
    "sm_2023_1_hypervisor": HypervisorCPUSSpec(
        cpu=CPUS["amd1"],
        cpu_count=2,
        numa_map=[list(range(64)), list(range(64, 128))],
        reserved_cores_per_node=1,
        threading_enabled=False,
    ),
    "g_2023_1": VirtualCPUSSpec(
        allocation_strategy=CPUAllocationStrategies.polite,
        cpu=CPU(name="AMD1", cores=1),
        cpu_count=20,
        threading_enabled=False,
    ),
    "c_2023_1": VirtualCPUSSpec(
        allocation_strategy=CPUAllocationStrategies.greedy,
        cpu=CPU(name="AMD1", cores=1),
        cpu_count=126,
        threading_enabled=False,
    ),
}


CONFIG_SPECS = {
    "hypervisor": ConfigSpec(
        role_name="hypervisor",
    ),
    "virtual_workstation": ConfigSpec(
        role_name="workstation",
    ),
    "virtual_compute": ConfigSpec(
        role_name="compute_node",
    ),
}


HOST_SPECS = {
    "sm_2023_1_hypervisor": HypervisorSpec(
        config=CONFIG_SPECS["hypervisor"],
        cpus=CPUS_SPECS["sm_2023_1_hypervisor"],
    ),
    "g_2023_1": VirtualSpec(
        config=CONFIG_SPECS["virtual_workstation"],
        cpus=CPUS_SPECS["g_2023_1"],
    ),
    "c_2023_1": VirtualSpec(
        config=CONFIG_SPECS["virtual_compute"],
        cpus=CPUS_SPECS["c_2023_1"],
    ),
}


def get_host_spec(name):
    if name not in HOST_SPECS:
        raise Exception(f"Not found:  {name} in HOST_SPECS")
    return HOST_SPECS[name]
