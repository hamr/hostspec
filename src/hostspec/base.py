from dataclasses import dataclass, field


@dataclass
class CPU:
    name: str   # cpu name from vendor
    cores: int


@dataclass
class HWSpec:
    """Spec of hardware config"""

    mem: int   # memory in MB
    cpus: list[CPU] = field(default_factory=list)
    gpus: list[str] = field(default_factory=list)  # list of strings for now, should be GPU objects
    # storage


@dataclass
class ConfigSpec:
    role_name: str


@dataclass
class HostSpec:
    """Top-level spec for host"""
    hw: HWSpec
    config: ConfigSpec


CPUS = {
    "amd_awesome": CPU(name="AMD awesome", cores=128),
}


HW_SPECS = {
    "sm_2023_1": HWSpec(
        cpus=[CPUS["amd_awesome"], CPUS["amd_awesome"]],
        mem=1000000,
    ),
}


CONFIG_SPECS = {
    "compute": ConfigSpec(role_name="compute"),
}


HOST_SPECS = {
    "sm_2023_1_compute": HostSpec(
        hw=HW_SPECS["sm_2023_1"],
        config=CONFIG_SPECS["compute"],
    ),
}


def register_cpu(name: str, **cpu_data) -> None:
    cpu = CPU(name=name, **cpu_data)
    CPUS[name] = cpu


def register_hw_spec(name: str, **hw_data) -> None:
    spec = HWSpec(**hw_data)
    HW_SPECS[name] = spec

