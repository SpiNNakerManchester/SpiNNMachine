# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spinn_machine import CoreSubset
from spinn_machine.config_setup import unittest_setup


def test_coresubset():
    unittest_setup()
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
    assert core_subset.__repr__() == ("0:0:OrderedSet([1, 2, 3, 4])")


def test_equals():
    unittest_setup()
    core_subset = CoreSubset(0, 0, [1, 2, 3])
    assert core_subset == CoreSubset(0, 0, [1, 2, 3])
    assert core_subset != CoreSubset(0, 1, [1, 2, 3])
    assert core_subset != CoreSubset(0, 0, [1])
    assert core_subset != "oops"


def test_in_dict():
    unittest_setup()
    cs1 = CoreSubset(0, 0, [1, 2, 3])
    cs2 = CoreSubset(0, 0, [4, 5, 6])
    cs3 = CoreSubset(0, 1, [1, 2, 3])
    cs4 = CoreSubset(0, 0, [1, 2, 3])
    cs5 = CoreSubset(0, 0, [1, 2, 3, 4])
    d = {}
    d[cs1] = 1
    d[cs2] = 2
    d[cs3] = 3
    d[cs4] = 4
    d[cs5] = 4
    assert len(d) == 4
