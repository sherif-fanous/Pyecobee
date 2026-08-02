def test_public_package_imports():
    import pyecobee

    assert pyecobee.EcobeeService is not None
    assert pyecobee.Utilities is not None
