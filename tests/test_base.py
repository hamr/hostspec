from hostspec import base


def test_instantiate_cpu_from_data():
    cpu_data = dict(name="AMD awesome", cores=128)
    base.CPU(**cpu_data)


def test_instantiate_cpus_spec_from_obj():
    cpu = base.CPU(name="AMD awesome", cores=128)
    base.CPUSSpec(cpu=cpu, cpu_count=2, threading_enabled=True)


def test_instantiate_host_spec_from_obj():
    cpu = base.CPU(name="AMD awesome", cores=128)
    cpus_spec = base.CPUSSpec(cpu=cpu, cpu_count=2, threading_enabled=True)
    config_spec = base.ConfigSpec(role_name="compute")
    base.HostSpec(config=config_spec, cpus=cpus_spec)
