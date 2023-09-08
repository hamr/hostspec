from dataclasses import dataclass, InitVar

from hostspec.defaults import get_host_spec
from hostspec.platform import HypervisorSpec, VirtualSpec
from hostspec.ops import assign_cpus


@dataclass
class Hypervisor:
    name: str
    spec: HypervisorSpec | None = None
    spec_name: InitVar[str | None] = None

    def __post_init__(self, spec_name):
        if self.spec is None and spec_name is not None:
            self.spec = get_host_spec(spec_name)


@dataclass
class Guest:
    name: str
    spec_name: InitVar[str]
    spec: VirtualSpec

    def __post_init__(self, spec_name):
        if self.spec is None and spec_name is not None:
            self.spec = get_host_spec(spec_name)


def test_config_fragment_c():
    request_data = {
        "hypervisor": dict(name="h1", spec_name="sm_2023_1_hypervisor"),
        "guests": [
            dict(name="g1", spec_name="c_2023_1"),
        ]
    }

    hypervisor = Hypervisor(**request_data["hypervisor"])
    guests = [Guest(**guest_data) for guest_data in request_data["guests"]]

    allocations = assign_cpus(hypervisor.spec, [g.spec for g in guests])
    print(h_spec.cpus)
