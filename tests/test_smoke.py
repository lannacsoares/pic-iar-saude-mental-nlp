import pic_iar


def test_package_imports():
    assert pic_iar.__version__


def test_models_registry():
    assert set(pic_iar.MODELS) == {"bertimbau", "xlmr", "mbert"}
