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
from spinn_machine import FixedRouteEntry
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException


class TestingFixedRouteEntries(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_fixed_route_creation(self):
        fre = FixedRouteEntry([1, 2, 3], [2, 3, 4])
        self.assertEqual(fre.__repr__(), "{2, 3, 4}:{1, 2, 3}")
        self.assertEqual(frozenset(fre.processor_ids), frozenset([1, 2, 3]))
        self.assertEqual(frozenset(fre.link_ids), frozenset([2, 3, 4]))

    def test_fixed_route_errors(self):
        with self.assertRaises(SpinnMachineAlreadyExistsException) as e:
            FixedRouteEntry([1, 2, 2], [2, 3, 4])
        self.assertEqual(e.exception.item, "processor ID")
        self.assertEqual(e.exception.value, "2")
        with self.assertRaises(SpinnMachineAlreadyExistsException) as e:
            FixedRouteEntry([1, 2, 3], [2, 3, 2])
        self.assertEqual(e.exception.item, "link ID")
        self.assertEqual(e.exception.value, "2")


if __name__ == '__main__':
    unittest.main()
