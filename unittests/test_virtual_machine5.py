# Copyright (c) 2014 The University of Manchester
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
from spinn_utilities.config_holder import set_config

from spinn_machine import virtual_machine
from spinn_machine.config_setup import unittest_setup
from spinn_machine.link_data_objects import SpinnakerLinkData
from spinn_machine.version import FIVE
from spinn_machine.version.version_5 import CHIPS_PER_BOARD


class TestVirtualMachine5(unittest.TestCase):

    VERSION_5_N_CORES_PER_BOARD = sum(CHIPS_PER_BOARD.values())

    def setUp(self):
        unittest_setup()

    def test_version_5(self):
        set_config("Machine", "version", FIVE)
        vm = virtual_machine(width=8, height=8)
        self.assertEqual(48, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))

        count = 0
        for _chip in vm.chips:
            for _link in _chip.router.links:
                count += 1
        self.assertEqual(240, count)
        self.assertEqual(120, vm.get_links_count())
#        self.assertEqual(str(vm),
#                         "[VirtualMachine: max_x=1, max_y=1, n_chips=4]")
        self.assertEqual(856, vm.get_cores_count())
        count = 0
        for _chip in vm.get_existing_xys_on_board(vm[1, 1]):
            count += 1
        self.assertEqual(48, count)
        self.assertEqual((0, 4), vm.get_unused_xy())

    def test_version_5_8_by_8(self):
        set_config("Machine", "version", FIVE)
        vm = virtual_machine(width=8, height=8, validate=True)
        self.assertEqual(48, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertTrue(vm.is_chip_at(4, 4))
        self.assertFalse(vm.is_chip_at(0, 4))
        self.assertFalse((0, 4) in list(vm.chip_coordinates))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(240, count)
        count = sum(_chip.n_processors for _chip in vm.chips)
        self.assertEqual(count, 856)
        spinnaker_links = (list(vm.spinnaker_links))
        expected = []
        sp = SpinnakerLinkData(0, 0, 0, 4, '127.0.0.0')
        expected.append((('127.0.0.0', 0), sp))
        expected.append((((0, 0), 0), sp))
        self.assertEqual(expected, spinnaker_links)
        # 8 links on each of the 6 sides recorded 3 times
        # Except for the Ethernet Chip's 3 links which are only recorded twice
        expected_fpgas = 8 * 6 * 3 - 3
        self.assertEqual(expected_fpgas, len(vm._fpga_links))
        keys = set([('127.0.0.0', 0, 0), ((7, 3), 0, 0), ((0, 0), 0, 0),
                    ('127.0.0.0', 0, 1), ((7, 3), 0, 1), ((0, 0), 0, 1),
                    ('127.0.0.0', 0, 2), ((6, 2), 0, 2), ((0, 0), 0, 2),
                    ('127.0.0.0', 0, 3), ((6, 2), 0, 3), ((0, 0), 0, 3),
                    ('127.0.0.0', 0, 4), ((5, 1), 0, 4), ((0, 0), 0, 4),
                    ('127.0.0.0', 0, 5), ((5, 1), 0, 5), ((0, 0), 0, 5),
                    ('127.0.0.0', 0, 6), ((4, 0), 0, 6), ((0, 0), 0, 6),
                    ('127.0.0.0', 0, 7), ((4, 0), 0, 7), ((0, 0), 0, 7),
                    ('127.0.0.0', 0, 8), ((4, 0), 0, 8), ((0, 0), 0, 8),
                    ('127.0.0.0', 0, 9), ((3, 0), 0, 9), ((0, 0), 0, 9),
                    ('127.0.0.0', 0, 10), ((3, 0), 0, 10), ((0, 0), 0, 10),
                    ('127.0.0.0', 0, 11), ((2, 0), 0, 11), ((0, 0), 0, 11),
                    ('127.0.0.0', 0, 12), ((2, 0), 0, 12), ((0, 0), 0, 12),
                    ('127.0.0.0', 0, 13), ((1, 0), 0, 13), ((0, 0), 0, 13),
                    ('127.0.0.0', 0, 14), ((1, 0), 0, 14), ((0, 0), 0, 14),
                    ('127.0.0.0', 0, 15), ((0, 0), 0, 15),
                    ('127.0.0.0', 1, 0), ((0, 0), 1, 0),
                    ('127.0.0.0', 1, 1), ((0, 0), 1, 1),
                    ('127.0.0.0', 1, 2), ((0, 1), 1, 2), ((0, 0), 1, 2),
                    ('127.0.0.0', 1, 3), ((0, 1), 1, 3), ((0, 0), 1, 3),
                    ('127.0.0.0', 1, 4), ((0, 2), 1, 4), ((0, 0), 1, 4),
                    ('127.0.0.0', 1, 5), ((0, 2), 1, 5), ((0, 0), 1, 5),
                    ('127.0.0.0', 1, 6), ((0, 3), 1, 6), ((0, 0), 1, 6),
                    ('127.0.0.0', 1, 7), ((0, 3), 1, 7), ((0, 0), 1, 7),
                    ('127.0.0.0', 1, 8), ((0, 3), 1, 8), ((0, 0), 1, 8),
                    ('127.0.0.0', 1, 9), ((1, 4), 1, 9), ((0, 0), 1, 9),
                    ('127.0.0.0', 1, 10), ((1, 4), 1, 10), ((0, 0), 1, 10),
                    ('127.0.0.0', 1, 11), ((2, 5), 1, 11), ((0, 0), 1, 11),
                    ('127.0.0.0', 1, 12), ((2, 5), 1, 12), ((0, 0), 1, 12),
                    ('127.0.0.0', 1, 13), ((3, 6), 1, 13), ((0, 0), 1, 13),
                    ('127.0.0.0', 1, 14), ((3, 6), 1, 14), ((0, 0), 1, 14),
                    ('127.0.0.0', 1, 15), ((4, 7), 1, 15), ((0, 0), 1, 15),
                    ('127.0.0.0', 2, 0), ((4, 7), 2, 0), ((0, 0), 2, 0),
                    ('127.0.0.0', 2, 1), ((4, 7), 2, 1), ((0, 0), 2, 1),
                    ('127.0.0.0', 2, 2), ((5, 7), 2, 2), ((0, 0), 2, 2),
                    ('127.0.0.0', 2, 3), ((5, 7), 2, 3), ((0, 0), 2, 3),
                    ('127.0.0.0', 2, 4), ((6, 7), 2, 4), ((0, 0), 2, 4),
                    ('127.0.0.0', 2, 5), ((6, 7), 2, 5), ((0, 0), 2, 5),
                    ('127.0.0.0', 2, 6), ((7, 7), 2, 6), ((0, 0), 2, 6),
                    ('127.0.0.0', 2, 7), ((7, 7), 2, 7), ((0, 0), 2, 7),
                    ('127.0.0.0', 2, 8), ((7, 7), 2, 8), ((0, 0), 2, 8),
                    ('127.0.0.0', 2, 9), ((7, 6), 2, 9), ((0, 0), 2, 9),
                    ('127.0.0.0', 2, 10), ((7, 6), 2, 10), ((0, 0), 2, 10),
                    ('127.0.0.0', 2, 11), ((7, 5), 2, 11), ((0, 0), 2, 11),
                    ('127.0.0.0', 2, 12), ((7, 5), 2, 12), ((0, 0), 2, 12),
                    ('127.0.0.0', 2, 13), ((7, 4), 2, 13), ((0, 0), 2, 13),
                    ('127.0.0.0', 2, 14), ((7, 4), 2, 14), ((0, 0), 2, 14),
                    ('127.0.0.0', 2, 15), ((7, 3), 2, 15), ((0, 0), 2, 15)])
        self.assertEqual(keys, set(vm._fpga_links.keys()))
        data = set()
        for (_, fpga_id, fpga_link), link in vm._fpga_links.items():
            data.add((link.connected_chip_x, link.connected_chip_y,
                      link.connected_link, fpga_id, fpga_link))
        expected = set([(7, 3, 0, 0, 0), (7, 3, 5, 0, 1), (6, 2, 0, 0, 2),
                        (6, 2, 5, 0, 3), (5, 1, 0, 0, 4), (5, 1, 5, 0, 5),
                        (4, 0, 0, 0, 6), (4, 0, 5, 0, 7), (4, 0, 4, 0, 8),
                        (3, 0, 5, 0, 9), (3, 0, 4, 0, 10), (2, 0, 5, 0, 11),
                        (2, 0, 4, 0, 12), (1, 0, 5, 0, 13), (1, 0, 4, 0, 14),
                        (0, 0, 5, 0, 15),
                        (0, 0, 4, 1, 0),  (0, 0, 3, 1, 1), (0, 1, 4, 1, 2),
                        (0, 1, 3, 1, 3), (0, 2, 4, 1, 4), (0, 2, 3, 1, 5),
                        (0, 3, 4, 1, 6), (0, 3, 3, 1, 7), (0, 3, 2, 1, 8),
                        (1, 4, 3, 1, 9), (1, 4, 2, 1, 10), (2, 5, 3, 1, 11),
                        (2, 5, 2, 1, 12), (3, 6, 3, 1, 13), (3, 6, 2, 1, 14),
                        (4, 7, 3, 1, 15),
                        (4, 7, 2, 2, 0), (4, 7, 1, 2, 1), (5, 7, 2, 2, 2),
                        (5, 7, 1, 2, 3), (6, 7, 2, 2, 4), (6, 7, 1, 2, 5),
                        (7, 7, 2, 2, 6), (7, 7, 1, 2, 7), (7, 7, 0, 2, 8),
                        (7, 6, 1, 2, 9), (7, 6, 0, 2, 10), (7, 5, 1, 2, 11),
                        (7, 5, 0, 2, 12), (7, 4, 1, 2, 13), (7, 4, 0, 2, 14),
                        (7, 3, 1, 2, 15)])
        self.assertEqual(data, expected)

    def test_version_5_12_by_12(self):
        set_config("Machine", "version", FIVE)
        vm = virtual_machine(height=12, width=12, validate=True)
        self.assertEqual(144, vm.n_chips)
        self.assertEqual(3, len(vm.ethernet_connected_chips))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(864, count)
        count = 0
        for _chip in vm.get_existing_xys_on_board(vm[1, 1]):
            count += 1
        self.assertEqual(48, count)
        self.assertEqual((12, 0), vm.get_unused_xy())
        spinnaker_links = (list(vm.spinnaker_links))
        expected = []
        self.assertEqual(expected, spinnaker_links)
        # 8 links on each of the 6 sides recorded 3 times
        # Except for the Ethernet Chip's 3 links which are only recorded twice
        expected_fpgas = (8 * 6 * 3 - 3) * 3
        self.assertEqual(expected_fpgas, len(vm._fpga_links))

    def test_version_5_16_by_16(self):
        set_config("Machine", "version", FIVE)
        vm = virtual_machine(height=16, width=16, validate=True)
        self.assertEqual(144, vm.n_chips)
        self.assertEqual(3, len(vm.ethernet_connected_chips))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(768, count)
        count = 0
        for _chip in vm.get_existing_xys_on_board(vm[1, 1]):
            count += 1
        self.assertEqual(48, count)
        self.assertEqual((0, 4), vm.get_unused_xy())
        spinnaker_links = (list(vm.spinnaker_links))
        expected = []
        sp = SpinnakerLinkData(0, 0, 0, 4, '127.0.0.0')
        expected.append((('127.0.0.0', 0), sp))
        expected.append((((0, 0), 0), sp))
        sp = SpinnakerLinkData(0, 4, 8, 4, '127.0.4.8')
        expected.append((('127.0.4.8', 0), sp))
        expected.append((((4, 8), 0), sp))
        self.assertEqual(expected, spinnaker_links)
        # 8 links on each of the 6 sides recorded 3 times
        # Except for the Ethernet Chip's 3 links which are only recorded twice
        expected_fpgas = (8 * 6 * 3 - 3) * 3
        self.assertEqual(expected_fpgas, len(vm._fpga_links))

    @staticmethod
    def _assert_fpga_link(machine, fpga, fpga_link, x, y, link_id, ip=None):
        link = machine.get_fpga_link_with_id(fpga, fpga_link, ip)
        assert link.connected_chip_x == x
        assert link.connected_chip_y == y
        assert link.connected_link == link_id

    def test_fpga_links_single_board(self):
        set_config("Machine", "version", FIVE)
        machine = virtual_machine(width=8, height=8)
        machine.add_fpga_links()
        self._assert_fpga_link(machine, 0, 0, 7, 3, 0)
        self._assert_fpga_link(machine, 0, 1, 7, 3, 5)
        self._assert_fpga_link(machine, 0, 2, 6, 2, 0)
        self._assert_fpga_link(machine, 0, 3, 6, 2, 5)
        self._assert_fpga_link(machine, 0, 4, 5, 1, 0)
        self._assert_fpga_link(machine, 0, 5, 5, 1, 5)
        self._assert_fpga_link(machine, 0, 6, 4, 0, 0)
        self._assert_fpga_link(machine, 0, 7, 4, 0, 5)

        self._assert_fpga_link(machine, 0, 8, 4, 0, 4)
        self._assert_fpga_link(machine, 0, 9, 3, 0, 5)
        self._assert_fpga_link(machine, 0, 10, 3, 0, 4)
        self._assert_fpga_link(machine, 0, 11, 2, 0, 5)
        self._assert_fpga_link(machine, 0, 12, 2, 0, 4)
        self._assert_fpga_link(machine, 0, 13, 1, 0, 5)
        self._assert_fpga_link(machine, 0, 14, 1, 0, 4)
        self._assert_fpga_link(machine, 0, 15, 0, 0, 5)

        self._assert_fpga_link(machine, 1, 0, 0, 0, 4)
        self._assert_fpga_link(machine, 1, 1, 0, 0, 3)
        self._assert_fpga_link(machine, 1, 2, 0, 1, 4)
        self._assert_fpga_link(machine, 1, 3, 0, 1, 3)
        self._assert_fpga_link(machine, 1, 4, 0, 2, 4)
        self._assert_fpga_link(machine, 1, 5, 0, 2, 3)
        self._assert_fpga_link(machine, 1, 6, 0, 3, 4)
        self._assert_fpga_link(machine, 1, 7, 0, 3, 3)

        self._assert_fpga_link(machine, 1, 8, 0, 3, 2)
        self._assert_fpga_link(machine, 1, 9, 1, 4, 3)
        self._assert_fpga_link(machine, 1, 10, 1, 4, 2)
        self._assert_fpga_link(machine, 1, 11, 2, 5, 3)
        self._assert_fpga_link(machine, 1, 12, 2, 5, 2)
        self._assert_fpga_link(machine, 1, 13, 3, 6, 3)
        self._assert_fpga_link(machine, 1, 14, 3, 6, 2)
        self._assert_fpga_link(machine, 1, 15, 4, 7, 3)

        self._assert_fpga_link(machine, 2, 0, 4, 7, 2)
        self._assert_fpga_link(machine, 2, 1, 4, 7, 1)
        self._assert_fpga_link(machine, 2, 2, 5, 7, 2)
        self._assert_fpga_link(machine, 2, 3, 5, 7, 1)
        self._assert_fpga_link(machine, 2, 4, 6, 7, 2)
        self._assert_fpga_link(machine, 2, 5, 6, 7, 1)
        self._assert_fpga_link(machine, 2, 6, 7, 7, 2)
        self._assert_fpga_link(machine, 2, 7, 7, 7, 1)

        self._assert_fpga_link(machine, 2, 8, 7, 7, 0)
        self._assert_fpga_link(machine, 2, 9, 7, 6, 1)
        self._assert_fpga_link(machine, 2, 10, 7, 6, 0)
        self._assert_fpga_link(machine, 2, 11, 7, 5, 1)
        self._assert_fpga_link(machine, 2, 12, 7, 5, 0)
        self._assert_fpga_link(machine, 2, 13, 7, 4, 1)
        self._assert_fpga_link(machine, 2, 14, 7, 4, 0)
        self._assert_fpga_link(machine, 2, 15, 7, 3, 1)

    def test_fpga_links_3_board(self):
        set_config("Machine", "version", FIVE)
        # A List of links, one for each side of each board in a 3-board toroid
        fpga_links = [("127.0.0.0", 0, 5, 5, 1, 5),
                      ("127.0.0.0", 0, 12, 2, 0, 4),
                      ("127.0.0.0", 1, 3, 0, 1, 3),
                      ("127.0.0.0", 1, 12, 2, 5, 2),
                      ("127.0.0.0", 2, 5, 6, 7, 1),
                      ("127.0.0.0", 2, 12, 7, 5, 0),
                      ("127.0.4.8", 0, 2, 10, 10, 0),
                      ("127.0.4.8", 0, 11, 6, 8, 5),
                      ("127.0.4.8", 1, 3, 4, 9, 3),
                      ("127.0.4.8", 1, 14, 7, 2, 2),
                      ("127.0.4.8", 2, 5, 10, 3, 1),
                      ("127.0.4.8", 2, 12, 11, 1, 0),
                      ("127.0.8.4", 0, 5, 1, 5, 5),
                      ("127.0.8.4", 0, 10, 11, 4, 4),
                      ("127.0.8.4", 1, 1, 8, 4, 3),
                      ("127.0.8.4", 1, 12, 10, 9, 2),
                      ("127.0.8.4", 2, 7, 3, 11, 1),
                      ("127.0.8.4", 2, 12, 3, 9, 0)]

        down_links = ":".join([f"{x},{y},{link}"
                              for _, _, _, x, y, link in fpga_links])
        set_config("Machine", "down_links", down_links)
        machine = virtual_machine(width=12, height=12)
        machine.add_fpga_links()
        for ip, fpga, fpga_link, x, y, link in fpga_links:
            self._assert_fpga_link(machine, fpga, fpga_link, x, y, link, ip)

    def test_none_triad(self):
        set_config("Machine", "version", FIVE)
        virtual_machine(width=20, height=16)
        virtual_machine(width=12, height=16)


if __name__ == '__main__':
    unittest.main()
