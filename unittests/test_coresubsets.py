from spinn_machine import CoreSubsets, CoreSubset


def test_coresubsets():
    core_subsets = CoreSubsets()
    assert len(core_subsets) == 0

    core_subsets.add_processor(0, 0, 1)
    assert len(core_subsets) == 1

    core_subsets.add_core_subset(CoreSubset(0, 0, [1]))
    assert len(core_subsets) == 1

    core_subsets.add_core_subset(CoreSubset(1, 0, [1, 2]))
    assert len(core_subsets) == 3
    assert core_subsets.is_chip(1, 0)
    assert core_subsets.is_core(0, 0, 1)
    assert not core_subsets.is_core(2, 0, 1)
    assert not core_subsets.is_chip(3, 1)
    assert not core_subsets.is_core(0, 0, 14)


def test_multiple():
    cs1 = CoreSubset(0, 0, [1, 2, 3])
    cs2 = CoreSubset(0, 0, [4, 5, 6])
    cs3 = CoreSubset(0, 1, [1, 2, 3])
    cs4 = CoreSubset(0, 0, [1, 2, 3])
    cs5 = CoreSubset(0, 0, [1, 2, 3, 4])
    css = CoreSubsets([cs1, cs2, cs3, cs4, cs5])
    assert (0, 1) in css
    assert (0, 0, 6) in css
    assert css.__repr__() == "(0, 0)(0, 1)"
    assert css[0, 1] == cs3


def test_iter():
    cs1 = CoreSubset(0, 0, [1, 2, 3])
    cs2 = CoreSubset(0, 0, [4, 5, 6])
    cs3 = CoreSubset(0, 1, [1, 2, 3])
    cs4 = CoreSubset(0, 0, [1, 2, 3])
    cs5 = CoreSubset(0, 0, [1, 2, 3, 4])
    css = CoreSubsets([cs1, cs2, cs3, cs4, cs5])

    for cs in css:
        assert 3 in cs
    for cs in css.core_subsets:
        assert 3 in cs

    assert len(css.get_core_subset_for_chip(1, 0)) == 0
