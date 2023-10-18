# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from spinn_machine import FrozenCoreSubsets, CoreSubset
from spinn_machine.config_setup import unittest_setup


class TestFrozenCoreSubsets(unittest.TestCase):

    def test_multiple(self):
        unittest_setup()
        cs1 = CoreSubset(0, 0, [1, 2, 3])
        cs2 = CoreSubset(0, 0, [4, 5, 6])
        cs3 = CoreSubset(0, 1, [1, 2, 3])
        cs4 = CoreSubset(0, 0, [1, 2, 3])
        cs5 = CoreSubset(0, 0, [1, 2, 3, 4])
        css = FrozenCoreSubsets([cs1, cs2, cs3])
        assert (0, 1) in css
        assert (0, 0, 6) in css
        assert css.__repr__() == "(0, 0)(0, 1)"
        assert css[0, 1] == cs3
        with self.assertRaises(RuntimeError):
            css.add_core_subset(cs4)
        with self.assertRaises(RuntimeError):
            css.add_core_subsets([cs4, cs5])
        with self.assertRaises(RuntimeError):
            css.add_processor(1, 2, 3)
