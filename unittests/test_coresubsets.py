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
