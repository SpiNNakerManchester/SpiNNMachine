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
from spinn_machine.link_data_objects import FPGALinkData, SpinnakerLinkData


class TestingLinks(unittest.TestCase):
    def test_fpga_link_data(self):
        ld = FPGALinkData(1, 2, 3, 4, 5, "somehost")
        ld2 = FPGALinkData(1, 2, 3, 4, 5, "somehost")
        ld3 = FPGALinkData(1, 2, 3, 4, 6, "somehost")
        self.assertEqual(ld.board_address, "somehost")
        self.assertEqual(ld.connected_chip_x, 3)
        self.assertEqual(ld.connected_chip_y, 4)
        self.assertEqual(ld.connected_link, 5)
        self.assertEqual(ld.fpga_id, 2)
        self.assertEqual(ld.fpga_link_id, 1)
        self.assertEqual(ld, ld2)
        self.assertNotEqual(ld, ld3)
        self.assertFalse(ld == "Foo")
        self.assertNotEqual(ld, "Foo")
        d = dict()
        d[ld] = 1
        d[ld2] = 2
        d[ld3] = 3
        self.assertEqual(len(d), 2)

    def test_spinnaker_link_data(self):
        ld = SpinnakerLinkData(2, 3, 4, 5, "somehost")
        ld2 = SpinnakerLinkData(2, 3, 4, 5, "somehost")
        ld3 = SpinnakerLinkData(2, 3, 4, 6, "somehost")
        self.assertEqual(ld.board_address, "somehost")
        self.assertEqual(ld.connected_chip_x, 3)
        self.assertEqual(ld.connected_chip_y, 4)
        self.assertEqual(ld.connected_link, 5)
        self.assertEqual(ld.spinnaker_link_id, 2)
        self.assertEqual(ld, ld2)
        self.assertNotEqual(ld, ld3)
        self.assertFalse(id == "Foo")
        self.assertNotEqual(ld, "Foo")
        d = dict()
        d[ld] = 1
        d[ld2] = 2
        d[ld3] = 3
        self.assertEqual(len(d), 2)


if __name__ == '__main__':
    unittest.main()
