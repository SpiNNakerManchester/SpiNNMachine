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
from spinn_machine.config_setup import unittest_setup
from spinn_machine.link_data_objects import FPGALinkData, SpinnakerLinkData


class TestingLinks(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_fpga_link_data(self) -> None:
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

    def test_spinnaker_link_data(self) -> None:
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
