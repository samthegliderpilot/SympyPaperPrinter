import pytest
import sympy_paper_printer as spp


@pytest.fixture(autouse=True)
def reset_config():
    # Snapshot current config, restore after each test
    old = spp.get_config()
    yield
    spp.configure(**old.__dict__)
