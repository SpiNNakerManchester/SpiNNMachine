from spinn_machine.core_subsets import CoreSubsets
from spinn_machine.core_subset import CoreSubset


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


def test_interest():
    cs11 = CoreSubset(0, 0, [1, 2, 3])
    cs12 = CoreSubset(0, 1, [1, 2, 3])
    cs13 = CoreSubset(1, 1, [1])
    cs14 = CoreSubset(2, 2, [1])
    css1 = CoreSubsets([cs11, cs12, cs13, cs14])
    cs21 = CoreSubset(0, 0, [2, 3, 5])
    cs22 = CoreSubset(1, 0, [1, 2, 3])
    cs23 = CoreSubset(1, 1, [9, 7, 1, 5])
    cs24 = CoreSubset(2, 2, [2])
    css2 = CoreSubsets([cs21, cs22, cs23, cs24])
    css3 = css1.intersect(css2)
    assert (0, 0, 2) in css3
    assert (0, 0, 3) in css3
    assert (1, 1, 1) in css3
    assert (8 == len(css1))
    assert (11 == len(css2))
    assert (3 == len(css3))
    assert css3.__repr__() == "(0, 0)(1, 1)"
