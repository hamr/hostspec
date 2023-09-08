from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CPU:
    cores: int
    name: str  # cpu name from vendor
    # threads: int


@dataclass
class CPUSSpec:
    cpu: CPU
    cpu_count: int
    threading_enabled: bool
    numa_map: list[list[int]] | None = None


@dataclass
class ConfigSpec:
    role_name: str


@dataclass
class HostSpec:
    """Top-level spec for host"""
    config: ConfigSpec
    cpus: CPUSSpec
