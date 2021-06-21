# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
