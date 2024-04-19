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
from spinn_machine.data import MachineDataView
from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.link_data_objects import SpinnakerLinkData
from spinn_machine.version.version_5 import CHIPS_PER_BOARD
from spinn_machine.virtual_machine import (
    virtual_machine_by_boards, virtual_machine_by_chips,
    virtual_machine_by_cores, virtual_machine_by_min_size)


class TestVirtualMachine5(unittest.TestCase):

    VERSION_5_N_CORES_PER_BOARD = sum(CHIPS_PER_BOARD.values())

    def setUp(self):
        unittest_setup()

    def test_illegal_vms(self):
        set_config("Machine", "version", 5)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=-1, height=2)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=2, height=-1)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=15, height=15)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(5, 7)
        size_x = 12 * 5
        size_y = 12 * 7
        with self.assertRaises(SpinnMachineException):
            virtual_machine(size_x + 1, size_y, validate=True)
        size_x = 12 * 5
        size_y = None
        with self.assertRaises(SpinnMachineException):
            virtual_machine(size_x, size_y, validate=True)

    def test_version_5(self):
        set_config("Machine", "version", 5)
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
        set_config("Machine", "version", 5)
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
        set_config("Machine", "version", 5)
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
        set_config("Machine", "version", 5)
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

    def test_version_5_hole(self):
        set_config("Machine", "version", 5)
        set_config("Machine", "down_chips", "3,3")
        vm = virtual_machine(height=8, width=8, validate=True)
        self.assertEqual(47, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertFalse(vm.is_link_at(3, 3, 2))
        self.assertFalse(vm.is_link_at(3, 2, 2))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        # 240 - 6 * 2
        self.assertEqual(228, count)
        self.assertEqual(48, len(list(vm.local_xys)))

    def test_version_5_hole2(self):
        set_config("Machine", "version", 5)
        set_config("Machine", "down_chips", "0,3")
        vm = virtual_machine(height=8, width=8, validate=True)
        self.assertEqual(47, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertFalse(vm.is_link_at(0, 2, 2))
        self.assertFalse(vm.is_link_at(1, 3, 3))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        # 240 - 3 * 2
        self.assertEqual(234, count)
        self.assertEqual(48, len(list(vm.local_xys)))
        self.assertEqual((0, 4), vm.get_unused_xy())

    def test_12_n_plus4_12_m_4(self):
        set_config("Machine", "version", 5)
        size_x = 12 * 5
        size_y = 12 * 7
        vm = virtual_machine(size_x + 4, size_y + 4, validate=True)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_12_n_12_m(self):
        set_config("Machine", "version", 5)
        size_x = 12 * 5
        size_y = 12 * 7
        vm = virtual_machine(size_x, size_y, validate=True)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_chips(self):
        set_config("Machine", "version", 5)
        vm = virtual_machine(8, 8)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(count, 48)

    def test_ethernet_chips_exist(self):
        set_config("Machine", "version", 5)
        vm = virtual_machine(width=48, height=24)
        for eth_chip in vm._ethernet_connected_chips:
            self.assertTrue(vm.get_chip_at(eth_chip.x, eth_chip.y),
                            "Eth chip location x={}, y={} not in "
                            "_configured_chips"
                            .format(eth_chip.x, eth_chip.y))

    def test_boot_chip(self):
        set_config("Machine", "version", 5)
        vm = virtual_machine(12, 12)
        # based on Chip equaling its XY
        self.assertEqual(vm.boot_chip, (0, 0))

    def test_get_chips_on_boards(self):
        set_config("Machine", "version", 5)
        vm = virtual_machine(width=24, height=36)
        # check each chip appears only once on the entire board
        count00 = 0
        count50 = 0
        count04 = 0
        count2436 = 0
        for eth_chip in vm._ethernet_connected_chips:
            list_of_chips = list(vm.get_existing_xys_on_board(eth_chip))
            self.assertEqual(len(list_of_chips), 48)
            if (0, 0) in list_of_chips:
                count00 += 1
            if (5, 0) in list_of_chips:
                count50 += 1
            if (0, 4) in list_of_chips:
                count04 += 1
            if (24, 36) in list_of_chips:
                count2436 += 1
        # (0,0), (5,0), (0,4) are all on this virtual machine
        self.assertEqual(count00, 1)
        self.assertEqual(count50, 1)
        self.assertEqual(count04, 1)

        # (24,36) is not on this virtual machine
        self.assertEqual(count2436, 0)

    @staticmethod
    def _assert_fpga_link(machine, fpga, fpga_link, x, y, link_id, ip=None):
        link = machine.get_fpga_link_with_id(fpga, fpga_link, ip)
        assert link.connected_chip_x == x
        assert link.connected_chip_y == y
        assert link.connected_link == link_id

    def test_fpga_links_single_board(self):
        set_config("Machine", "version", 5)
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
        set_config("Machine", "version", 5)
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

    def test_big(self):
        set_config("Machine", "version", 5)
        virtual_machine(
            width=240, height=240, validate=True)

    def test_48_28(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(48, 24, validate=True)
        global_xys = set()
        for chip in machine.chips:
            local_x, local_y = machine.get_local_xy(chip)
            global_x, global_y = machine.get_global_xy(
                local_x, local_y,
                chip.nearest_ethernet_x, chip.nearest_ethernet_y)
            self.assertEqual(global_x, chip.x)
            self.assertEqual(global_y, chip.y)
            global_xys.add((global_x, global_y))
        self.assertEqual(len(global_xys), 48 * 24)
        self.assertEqual(48, len(list(machine.local_xys)))

    def test_48_24(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(48, 24, validate=True)
        global_xys = set()
        for chip in machine.chips:
            local_x, local_y = machine.get_local_xy(chip)
            global_x, global_y = machine.get_global_xy(
                local_x, local_y,
                chip.nearest_ethernet_x, chip.nearest_ethernet_y)
            self.assertEqual(global_x, chip.x)
            self.assertEqual(global_y, chip.y)
            global_xys.add((global_x, global_y))
        self.assertEqual(len(global_xys), 48 * 24)
        self.assertEqual(48, len(list(machine.local_xys)))

    def test_52_28(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(48, 24, validate=True)
        global_xys = set()
        for chip in machine.chips:
            local_x, local_y = machine.get_local_xy(chip)
            global_x, global_y = machine.get_global_xy(
                local_x, local_y,
                chip.nearest_ethernet_x, chip.nearest_ethernet_y)
            self.assertEqual(global_x, chip.x)
            self.assertEqual(global_y, chip.y)
            global_xys.add((global_x, global_y))
        self.assertEqual(len(global_xys), 48 * 24)
        self.assertEqual(48, len(list(machine.local_xys)))

    def test_52_24(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(48, 24, validate=True)
        global_xys = set()
        for chip in machine.chips:
            local_x, local_y = machine.get_local_xy(chip)
            global_x, global_y = machine.get_global_xy(
                local_x, local_y,
                chip.nearest_ethernet_x, chip.nearest_ethernet_y)
            self.assertEqual(global_x, chip.x)
            self.assertEqual(global_y, chip.y)
            global_xys.add((global_x, global_y))
        self.assertEqual(len(global_xys), 48 * 24)
        self.assertEqual(48, len(list(machine.local_xys)))

    def test_fullwrap_holes(self):
        set_config("Machine", "version", 5)
        hole = [(1, 1), (7, 7), (8, 1), (8, 10), (1, 8), (9, 6)]
        hole_str = ":".join([f"{x},{y}" for x, y in hole])
        set_config("Machine", "down_chips", hole_str)
        machine = virtual_machine(12, 12, validate=True)
        # Board 0,0
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(0, 0))))
        count = 0
        for chip in machine.get_chips_by_ethernet(0, 0):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(0, 0):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_down_xys_by_ethernet(0, 0):
            count += 1
            assert xy in hole
        self.assertEqual(2, count)
        # Board 4, 8
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(4, 8))))
        count = 0
        for chip in machine.get_chips_by_ethernet(4, 8):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(4, 8):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)
        # Board 8,4
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(8, 4))))
        count = 0
        for chip in machine.get_chips_by_ethernet(8, 4):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(8, 4):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)

    def test_horizontal_wrap_holes(self):
        set_config("Machine", "version", 5)
        hole = [(1, 1), (7, 7), (8, 13), (8, 10), (1, 8), (9, 6)]
        hole_str = ":".join([f"{x},{y}" for x, y in hole])
        set_config("Machine", "down_chips", hole_str)
        machine = virtual_machine(12, 16, validate=True)
        # Board 0,0
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(0, 0))))
        count = 0
        for chip in machine.get_chips_by_ethernet(0, 0):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(0, 0):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_down_xys_by_ethernet(0, 0):
            count += 1
            assert xy in hole
        self.assertEqual(2, count)
        # Board 4, 8
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(4, 8))))
        count = 0
        for chip in machine.get_chips_by_ethernet(4, 8):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(4, 8):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)
        # Board 8,4
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(8, 4))))
        count = 0
        for chip in machine.get_chips_by_ethernet(8, 4):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(8, 4):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)

    def test_vertical_wrap_holes(self):
        set_config("Machine", "version", 5)
        hole = [(1, 1), (7, 7), (8, 1), (8, 10), (13, 8), (9, 6)]
        hole_str = ":".join([f"{x},{y}" for x, y in hole])
        set_config("Machine", "down_chips", hole_str)
        machine = virtual_machine(16, 12, validate=True)
        # Board 0,0
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(0, 0))))
        count = 0
        for chip in machine.get_chips_by_ethernet(0, 0):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(0, 0):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_down_xys_by_ethernet(0, 0):
            count += 1
            assert xy in hole
        self.assertEqual(2, count)
        # Board 4, 8
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(4, 8))))
        count = 0
        for chip in machine.get_chips_by_ethernet(4, 8):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(4, 8):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)
        # Board 8,4
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(8, 4))))
        count = 0
        for chip in machine.get_chips_by_ethernet(8, 4):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(8, 4):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)

    def test_no_wrap_holes(self):
        set_config("Machine", "version", 5)
        hole = [(1, 1), (7, 7), (8, 13), (8, 10), (13, 8), (9, 6)]
        hole_str = ":".join([f"{x},{y}" for x, y in hole])
        set_config("Machine", "down_chips", hole_str)
        machine = virtual_machine(16, 16, validate=True)
        # Board 0,0
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(0, 0))))
        count = 0
        for chip in machine.get_chips_by_ethernet(0, 0):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(0, 0):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_down_xys_by_ethernet(0, 0):
            count += 1
            assert xy in hole
        self.assertEqual(2, count)
        # Board 4, 8
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(4, 8))))
        count = 0
        for chip in machine.get_chips_by_ethernet(4, 8):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(4, 8):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)
        # Board 8,4
        self.assertEqual(48, len(list(machine.get_xys_by_ethernet(8, 4))))
        count = 0
        for chip in machine.get_chips_by_ethernet(8, 4):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(46, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(8, 4):
            count += 1
            assert xy not in hole
        self.assertEqual(46, count)

    def test_n_cores_full_wrap(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(12, 12)
        n_cores = sum(
            n_cores
            for (_, n_cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD * 3)

    def test_n_cores_no_wrap(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(16, 16)
        n_cores = sum(
            n_cores
            for (_, n_cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD * 3)
        chip34 = machine.get_chip_at(3, 4)
        where = machine.where_is_chip(chip34)
        self.assertEqual(
            where, 'global chip 3, 4 on 127.0.0.0 is chip 3, 4 on 127.0.0.0')
        chip1112 = machine[11, 12]
        where = machine.where_is_chip(chip1112)
        self.assertEqual(
            where, 'global chip 11, 12 on 127.0.0.0 is chip 7, 4 on 127.0.4.8')
        where = machine.where_is_xy(10, 5)
        self.assertEqual(
            where, 'global chip 10, 5 on 127.0.0.0 is chip 2, 1 on 127.0.8.4')
        where = machine.where_is_xy(15, 15)
        self.assertEqual(where, 'No chip 15, 15 found')

    def test_n_cores_horizontal_wrap(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(12, 16)
        n_cores = sum(
            n_cores
            for (_, n_cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD * 3)

    def test_n_cores_vertical_wrap(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(12, 16)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD * 3)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD * 3)

    def test_n_cores_8_8(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(8, 8)
        n_cores = sum(
            cores for (_, cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, self.VERSION_5_N_CORES_PER_BOARD)

    def test_8_8_by_cores_1_board(self):
        set_config("Machine", "version", 5)
        version = MachineDataView.get_machine_version()
        n_cores = sum(version.chip_core_map.values())
        n_cores -= version.n_chips_per_board
        machine = virtual_machine_by_cores(n_cores)
        self.assertEqual(8, machine.width)
        self.assertEqual(8, machine.height)
        self.assertEqual(n_cores, machine.total_available_user_cores)
        machine = virtual_machine_by_boards(1)
        self.assertEqual(8, machine.width)
        self.assertEqual(8, machine.height)
        self.assertEqual(n_cores, machine.total_available_user_cores)

    def test_8_8_by_cores_3_boards(self):
        set_config("Machine", "version", 5)
        version = MachineDataView.get_machine_version()
        n_cores = sum(version.chip_core_map.values())
        n_cores -= version.n_chips_per_board
        machine = virtual_machine_by_cores(n_cores * 2)
        # despite asking for two boards you get a triad
        self.assertEqual(16, machine.width)
        self.assertEqual(16, machine.height)
        self.assertEqual(n_cores*3, machine.total_available_user_cores)
        machine = virtual_machine_by_boards(2)
        # despite asking for two boards you get a triad
        self.assertEqual(16, machine.width)
        self.assertEqual(16, machine.height)
        self.assertEqual(n_cores*3, machine.total_available_user_cores)
        machine = virtual_machine_by_chips(100)
        # despite asking for two boards you get a triad
        self.assertEqual(16, machine.width)
        self.assertEqual(16, machine.height)
        self.assertEqual(n_cores*3, machine.total_available_user_cores)

    def test_8_8_by_cores_6_boards(self):
        set_config("Machine", "version", 5)
        version = MachineDataView.get_machine_version()
        n_cores = sum(version.chip_core_map.values())
        n_cores -= version.n_chips_per_board
        machine = virtual_machine_by_cores(n_cores * 5)
        self.assertEqual(28, machine.width)
        self.assertEqual(16, machine.height)
        self.assertEqual(n_cores * 6, machine.total_available_user_cores)
        machine = virtual_machine_by_boards(4)
        self.assertEqual(28, machine.width)
        self.assertEqual(16, machine.height)
        self.assertEqual(n_cores * 6, machine.total_available_user_cores)

    def test_8_8_by_cores_12_boards(self):
        set_config("Machine", "version", 5)
        version = MachineDataView.get_machine_version()
        n_cores = sum(version.chip_core_map.values())
        n_cores -= version.n_chips_per_board
        machine = virtual_machine_by_cores(n_cores * 9)
        self.assertEqual(28, machine.width)
        self.assertEqual(28, machine.height)
        self.assertEqual(n_cores * 12, machine.total_available_user_cores)
        machine = virtual_machine_by_boards(10)
        self.assertEqual(28, machine.width)
        self.assertEqual(28, machine.height)
        self.assertEqual(n_cores * 12, machine.total_available_user_cores)

    def test_8_8_by_cores_18_boards(self):
        set_config("Machine", "version", 5)
        version = MachineDataView.get_machine_version()
        n_cores = sum(version.chip_core_map.values())
        n_cores -= version.n_chips_per_board
        machine = virtual_machine_by_cores(n_cores * 12 + 1)
        self.assertEqual(40, machine.width)
        self.assertEqual(28, machine.height)
        self.assertEqual(n_cores * 18, machine.total_available_user_cores)
        machine = virtual_machine_by_boards(15)
        self.assertEqual(40, machine.width)
        self.assertEqual(28, machine.height)
        self.assertEqual(n_cores * 18, machine.total_available_user_cores)

    def test_by_min_size(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine_by_min_size(15, 21)
        self.assertGreaterEqual(machine.width, 15)
        self.assertGreaterEqual(machine.height, 21)

    def test_by_min_size_edge_case(self):
        set_config("Machine", "version", 5)
        version = MachineDataView.get_machine_version()
        width, height = version.board_shape
        machine = virtual_machine_by_min_size(width, height + 1)
        self.assertGreaterEqual(machine.width, width)
        self.assertGreaterEqual(machine.height, height + 1)


if __name__ == '__main__':
    unittest.main()
