import sympy_paper_printer as spp


def test_configure_changes_global_config():
    spp.configure(silent=True, clean_equations=False)
    cfg = spp.get_config()
    assert cfg.silent is True
    assert cfg.clean_equations is False


def test_configured_context_manager_restores():
    before = spp.get_config()
    assert before.clean_equations is True  # default from our rewrite

    with spp.configured(clean_equations=False):
        assert spp.get_config().clean_equations is False

    after = spp.get_config()
    assert after.clean_equations == before.clean_equations
    assert after.silent == before.silent
