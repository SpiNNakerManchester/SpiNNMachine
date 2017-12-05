from spinn_machine.core_subset import CoreSubset


def test_coresubset():
    core_subset = CoreSubset(0, 0, [1, 2, 3])
    assert len(core_subset) == 3
    assert core_subset.x == 0
    assert core_subset.y == 0
    assert 2 in core_subset

    core_subset.add_processor(3)
    assert len(core_subset) == 3

    core_subset.add_processor(4)
    assert len(core_subset) == 4

    assert list(core_subset.processor_ids) == [1, 2, 3, 4]


def test_equals():
    core_subset = CoreSubset(0, 0, [1, 2, 3])
    assert core_subset == CoreSubset(0, 0, [1, 2, 3])
    assert core_subset != CoreSubset(0, 1, [1, 2, 3])
    assert core_subset != CoreSubset(0, 0, [1])
