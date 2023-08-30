from hostspec import base


def test_instantiate_cpu_from_data():
    cpu_data = dict(name="AMD awesome", cores=128)
    cpu = base.CPU(**cpu_data)


def test_instantiate_hw_spec_from_obj():
    cpu = base.CPU(name="AMD awesome", cores=128)
    hw_spec = base.HWSpec(cpus=[cpu, cpu], mem=1000000)


def test_instantiate_hw_spec_from_data():
    cpu_data = dict(name="AMD awesome", cores=128)
    hw_data = dict(
        cpus=[cpu_data, cpu_data],
        mem=1000000,
    )
    hw_spec = base.HWSpec(**hw_data)


def test_instantiate_host_spec_from_obj():
    cpu = base.CPU(name="AMD awesome", cores=128)
    hw = base.HWSpec(cpus=[cpu, cpu], mem=1000000)
    config = base.ConfigSpec(role_name="compute")
    spec = base.HostSpec(config=config, hw=hw)


def test_instantiate_host_spec_from_data():
    config_data = dict(role_name="compute")
    cpu_data = dict(name="AMD awesome", cores=128)
    host_spec_data = dict(
        config=config_data,
        hw=dict(cpus=[cpu_data, cpu_data], mem=1000000),
    )
    host_spec = base.HostSpec(**host_spec_data)


def test_get_host_spec():
    spec = base.HOST_SPECS["sm_2023_1_compute"]


def test_register_cpu():
    base.register_cpu("AMD better", cores=256)
    assert "AMD better" in base.CPUS


def test_add_register_hw_spec():
    spec_name = "sm_2023_2"
    cpu = base.CPUS["amd_awesome"]
    base.register_hw_spec(spec_name, cpus=[cpu, cpu], mem=500000)
    assert spec_name in base.HW_SPECS
