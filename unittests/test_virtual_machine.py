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
from spinn_machine.config_setup import unittest_setup
from spinn_machine import Chip, Link, Router, virtual_machine
from spinn_machine.exceptions import (
    SpinnMachineException, SpinnMachineAlreadyExistsException)
from spinn_machine.ignores import IgnoreChip, IgnoreCore, IgnoreLink
from spinn_machine.machine_factory import machine_repair
from spinn_machine.version.version_5 import CHIPS_PER_BOARD
from .geometry import (to_xyz, shortest_mesh_path_length,
                       shortest_torus_path_length, minimise_xyz)


class TestVirtualMachine(unittest.TestCase):

    VERSION_5_N_CORES_PER_BOARD = sum(CHIPS_PER_BOARD.values())

    def setUp(self):
        unittest_setup()

    def _create_chip(self, x, y):
        # Create a list of processors.

        n_processors = 18

        links = list()
        links.append(Link(0, 0, 0, 1, 1))
        links.append(Link(0, 1, 1, 1, 0))
        links.append(Link(1, 1, 2, 0, 0))
        links.append(Link(1, 0, 3, 0, 1))
        _router = Router(links, 1024)

        _sdram = 128
        nearest_ethernet_chip = (0, 0)
        _ip = "192.162.240.253"

        if (x == y == 0):
            return Chip(x, y, n_processors, _router, _sdram,
                        nearest_ethernet_chip[0],
                        nearest_ethernet_chip[1], _ip)
        else:
            return Chip(x, y, n_processors, _router, _sdram,
                        nearest_ethernet_chip[0],
                        nearest_ethernet_chip[1], None)

    def test_illegal_vms(self):
        set_config("Machine", "version", 5)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=-1, height=2)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=2, height=-1)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=15, height=15)

    def test_version_2(self):
        set_config("Machine", "version", 2)
        vm = virtual_machine(width=2, height=2)
        self.assertEqual(4, vm.n_chips)
        self.assertTrue(vm.is_chip_at(0, 0))
        self.assertTrue(vm.is_chip_at(0, 1))
        self.assertTrue(vm.is_chip_at(1, 0))
        self.assertTrue(vm.is_chip_at(1, 1))
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertTrue(vm.is_link_at(0, 0, 0))
        self.assertTrue(vm.is_link_at(0, 0, 1))
        self.assertTrue(vm.is_link_at(0, 0, 2))
        self.assertFalse(vm.is_link_at(0, 0, 3))
        self.assertFalse(vm.is_link_at(0, 0, 4))
        self.assertTrue(vm.is_link_at(0, 0, 5))
        self.assertTrue(vm.is_link_at(0, 1, 0))
        self.assertTrue(vm.is_link_at(0, 1, 1))
        self.assertTrue(vm.is_link_at(0, 1, 2))
        self.assertFalse(vm.is_link_at(0, 1, 3))
        self.assertFalse(vm.is_link_at(0, 1, 4))
        self.assertTrue(vm.is_link_at(0, 1, 5))

        self.assertFalse(vm.is_link_at(1, 0, 0))
        self.assertFalse(vm.is_link_at(1, 0, 1))
        self.assertTrue(vm.is_link_at(1, 0, 2))
        self.assertTrue(vm.is_link_at(1, 0, 3))
        self.assertTrue(vm.is_link_at(1, 0, 4))
        self.assertTrue(vm.is_link_at(1, 0, 5))
        self.assertFalse(vm.is_link_at(1, 1, 0))
        self.assertFalse(vm.is_link_at(1, 1, 1))
        self.assertTrue(vm.is_link_at(1, 1, 2))
        self.assertTrue(vm.is_link_at(1, 1, 3))
        self.assertTrue(vm.is_link_at(1, 1, 4))
        self.assertTrue(vm.is_link_at(1, 1, 5))

        count = 0
        for _chip in vm.chips:
            for _link in _chip.router.links:
                count += 1
        self.assertEqual(16, count)
#        self.assertEqual(str(vm),
#                         "[VirtualMachine: max_x=1, max_y=1, n_chips=4]")
        self.assertEqual(72, vm.get_cores_count())
        self.assertEqual(8, vm.get_links_count())
        count = 0
        for _chip in vm.get_existing_xys_on_board(vm.get_chip_at(1, 1)):
            count += 1
        self.assertEqual(4, count)
        self.assertEqual((2, 0), vm.get_unused_xy())

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

    def test_version_5_12_by_12(self):
        set_config("Machine", "version", 5)
        vm = virtual_machine(height=12, width=12, validate=True)
        self.assertEqual(144, vm.n_chips)
        self.assertEqual(3, len(vm.ethernet_connected_chips))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(864, count)
        count = 0
        for _chip in vm.get_existing_xys_on_board(vm.get_chip_at(1, 1)):
            count += 1
        self.assertEqual(48, count)
        self.assertEqual((12, 0), vm.get_unused_xy())

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
        self.assertEqual(48, len(vm.local_xys))

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
        self.assertEqual(48, len(vm.local_xys))
        self.assertEqual((0, 4), vm.get_unused_xy())

    def test_new_vm_with_monitor(self):
        set_config("Machine", "version", 2)
        n_cpus = 13
        vm = virtual_machine(2, 2, n_cpus_per_chip=n_cpus, validate=True)
        _chip = vm.get_chip_at(1, 1)
        self.assertEqual(n_cpus, _chip.n_processors)
        monitors = 0
        normal = 0
        for core in _chip.processors:
            if core.is_monitor:
                monitors += 1
            else:
                normal += 1
        self.assertEqual(n_cpus - 1, normal)
        self.assertEqual(1, monitors)

    def test_iter_chips(self):
        set_config("Machine", "version", 2)
        vm = virtual_machine(2, 2)
        self.assertEqual(4, vm.n_chips)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(4, count)

    def test_down_chip(self):
        set_config("Machine", "version", 2)
        down_chips = set()
        down_chips.add((1, 1))
        set_config("Machine", "down_chips", "1,1")
        vm = virtual_machine(2, 2)
        self.assertEqual(3, vm.n_chips)
        count = 0
        for _chip in vm.chip_coordinates:
            count += 1
            self.assertNotIn(_chip, down_chips)
        self.assertEqual(3, count)

    def test_add_existing_chip(self):
        set_config("Machine", "version", 2)
        vm = virtual_machine(2, 2)
        _chip = self._create_chip(1, 1)
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            vm.add_chip(_chip)

    def test_weird_size(self):
        with self.assertRaises(SpinnMachineException):
            virtual_machine(5, 7)

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

    def test_bad_size(self):
        set_config("Machine", "version", 5)
        size_x = 12 * 5
        size_y = 12 * 7
        with self.assertRaises(SpinnMachineException):
            virtual_machine(size_x + 1, size_y, validate=True)

    def test_none_size(self):
        set_config("Machine", "version", 5)
        size_x = 12 * 5
        size_y = None
        with self.assertRaises(SpinnMachineException):
            virtual_machine(size_x, size_y, validate=True)

    def test_add__chip(self):
        set_config("Machine", "version", 2)
        vm = virtual_machine(2, 2)
        _chip = self._create_chip(2, 2)
        vm.add_chip(_chip)
        self.assertEqual(5, vm.n_chips)

        self.assertTrue(vm.is_chip_at(2, 2))
        _good = vm.get_chip_at(2, 2)
        self.assertEqual(_chip, _good)

        _bad = vm.get_chip_at(2, 1)
        self.assertIsNone(_bad)

        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(5, count)

    def test_add_high_chip_with_down(self):
        set_config("Machine", "version", 2)
        set_config("Machine", "down_chips", "1,1")
        vm = virtual_machine(2, 2)
        self.assertEqual(3, vm.n_chips)

        _chip = self._create_chip(2, 2)
        vm.add_chip(_chip)
        self.assertEqual(4, vm.n_chips)

        self.assertTrue(vm.is_chip_at(2, 2))
        _good = vm.get_chip_at(2, 2)
        self.assertEqual(_chip, _good)

        _bad = vm.get_chip_at(2, 1)
        self.assertIsNone(_bad)

        _down = vm.get_chip_at(1, 1)
        self.assertIsNone(_down)

        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(4, count)

    def test_add_low_chip_with_down(self):
        set_config("Machine", "version", 2)
        set_config("Machine", "down_chips", "1,1")
        vm = virtual_machine(2, 2)
        self.assertEqual(3, vm.n_chips)
        self.assertFalse(vm.is_chip_at(1, 1))

        _chip = self._create_chip(1, 1)
        vm.add_chip(_chip)
        self.assertEqual(4, vm.n_chips)

        self.assertTrue(vm.is_chip_at(1, 1))
        _good = vm.get_chip_at(1, 1)
        self.assertEqual(_chip, _good)

        _bad = vm.get_chip_at(2, 1)
        self.assertIsNone(_bad)

        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(4, count)

    def test_chips(self):
        set_config("Machine", "version", 2)
        vm = virtual_machine(2, 2)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(count, 4)

    def test_ethernet_chips_exist(self):
        set_config("Machine", "version", 5)
        vm = virtual_machine(width=48, height=24)
        for eth_chip in vm._ethernet_connected_chips:
            self.assertTrue(vm.get_chip_at(eth_chip.x, eth_chip.y),
                            "Eth chip location x={}, y={} not in "
                            "_configured_chips"
                            .format(eth_chip.x, eth_chip.y))

    def test_boot_chip(self):
        set_config("Machine", "version", 2)
        vm = virtual_machine(2, 2)
        self.assertNotEqual(vm.boot_chip, None)

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

    def test_size_2_2(self):
        set_config("Machine", "version", 2)
        machine = virtual_machine(2, 2, validate=True)
        ethernet = machine.get_chip_at(0, 0)
        chips = set(machine.get_existing_xys_on_board(ethernet))
        self.assertEqual(len(chips), 4)
        chips = set(machine.get_existing_xys_by_ethernet(0, 0))
        self.assertEqual(len(chips), 4)
        global_xys = set()
        for chip in machine.chips:
            local_x, local_y = machine.get_local_xy(chip)
            global_x, global_y = machine.get_global_xy(
                local_x, local_y,
                chip.nearest_ethernet_x, chip.nearest_ethernet_y)
            self.assertEqual(global_x, chip.x)
            self.assertEqual(global_y, chip.y)
            global_xys.add((global_x, global_y))
        self.assertEqual(len(global_xys), 4)
        self.assertEqual(4, len(machine.local_xys))

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
        self.assertEqual(48, len(machine.local_xys))

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
        self.assertEqual(48, len(machine.local_xys))

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
        self.assertEqual(48, len(machine.local_xys))

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
        self.assertEqual(48, len(machine.local_xys))

    def test_size_2_2_hole(self):
        set_config("Machine", "version", 2)
        hole = [(1, 1)]
        set_config("Machine", "down_chips", "1,1")
        machine = virtual_machine(2, 2, validate=True)
        self.assertEqual(4, len(list(machine.get_xys_by_ethernet(0, 0))))
        count = 0
        for chip in machine.get_chips_by_ethernet(0, 0):
            count += 1
            xy = (chip.x, chip.y)
            assert xy not in hole
        self.assertEqual(3, count)
        count = 0
        for xy in machine.get_existing_xys_by_ethernet(0, 0):
            count += 1
            assert xy not in hole
        self.assertEqual(3, count)

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

    def _check_path(self, source, target, path, width, height):
        new_target = ((source[0] + path[0] - path[2]) % width,
                      (source[1] + path[1] - path[2]) % height)
        self.assertEqual(target, new_target, "{}{}".format(source, path))

    def test_nowrap_shortest_path(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(16, 28, validate=True)
        for source in machine.chip_coordinates:
            for target in machine.chip_coordinates:
                rig_len = shortest_mesh_path_length(
                    to_xyz(source), to_xyz(target))
                mac_len = machine.get_vector_length(source, target)
                self.assertEqual(rig_len, mac_len)
                path = machine.get_vector(source, target)
                self.assertEqual(
                    mac_len, abs(path[0]) + abs(path[1]) + abs(path[2]))
                self._check_path(source, target, path, 1000000, 1000000)

    def test_fullwrap_shortest_path(self):
        set_config("Machine", "version", 5)
        width = 12
        height = 24
        machine = virtual_machine(width, height, validate=True)
        for source in machine.chip_coordinates:
            for target in machine.chip_coordinates:
                rig_len = shortest_torus_path_length(
                    to_xyz(source), to_xyz(target), width, height)
                mac_len = machine.get_vector_length(source, target)
                self.assertEqual(rig_len, mac_len)
                path = machine.get_vector(source, target)
                self.assertEqual(
                    mac_len, abs(path[0]) + abs(path[1]) + abs(path[2]),
                    "{}{}{}".format(source, target, path))
                self._check_path(source, target, path, width, height)

    def test_hoizontal_wrap_shortest_path(self):
        set_config("Machine", "version", 5)
        width = 12
        height = 16
        machine = virtual_machine(width, height, validate=False)
        for source in machine.chip_coordinates:
            for target in machine.chip_coordinates:
                rig_no = shortest_mesh_path_length(
                    to_xyz(source), to_xyz(target))
                if source[0] < target[0]:
                    fake = (target[0] - width, target[1])
                else:
                    fake = (target[0] + width, target[1])
                rig_with = shortest_mesh_path_length(
                    to_xyz(source), to_xyz(fake))
                rig_len = min(rig_no, rig_with)
                mac_len = machine.get_vector_length(source, target)
                self.assertEqual(rig_len, mac_len, "{} {}".format(
                    source, target))
                path = machine.get_vector(source, target)
                self.assertEqual(
                    mac_len, abs(path[0]) + abs(path[1]) + abs(path[2]),
                    "{}{}{}".format(source, target, path))
                self._check_path(source, target, path, width, height)

    def test_vertical_wrap_shortest_path(self):
        set_config("Machine", "version", 5)
        width = 16
        height = 12
        machine = virtual_machine(width, height, validate=False)
        for source in machine.chip_coordinates:
            for target in machine.chip_coordinates:
                rig_no = shortest_mesh_path_length(
                    to_xyz(source), to_xyz(target))
                if source[1] < target[1]:
                    fake = (target[0], target[1] - height)
                else:
                    fake = (target[0], target[1] + height)
                rig_with = shortest_mesh_path_length(
                    to_xyz(source), to_xyz(fake))
                rig_len = min(rig_no, rig_with)
                mac_len = machine.get_vector_length(source, target)
                self.assertEqual(rig_len, mac_len, "{} {}".format(
                    source, target))
                path = machine.get_vector(source, target)
                self.assertEqual(
                    mac_len, abs(path[0]) + abs(path[1]) + abs(path[2]),
                    "{}{}{}".format(source, target, path))
                self._check_path(source, target, path, width, height)

    def test_minimize(self):
        set_config("Machine", "version", 3)
        machine = virtual_machine(2, 2, validate=False)
        for x in range(-3, 3):
            for y in range(-3, 3):
                min1 = minimise_xyz((x, y, 0))
                min2 = machine._minimize_vector(x, y)
                self.assertEqual(min1, min2)

    def test_unreachable_incoming_chips(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(8, 8)

        # Delete links incoming to 3, 3
        down_links = [
            (2, 2, 1), (2, 3, 0), (3, 4, 5), (4, 4, 4), (4, 3, 3), (3, 2, 2)]
        for (x, y, link) in down_links:
            if machine.is_link_at(x, y, link):
                del machine._chips[x, y].router._links[link]
        unreachable = machine.unreachable_incoming_chips()
        self.assertListEqual([(3, 3)], unreachable)

    def test_unreachable_outgoing_chips(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(8, 8)

        # Delete links outgoing from 3, 3
        for link in range(6):
            if machine.is_link_at(3, 3, link):
                del machine._chips[3, 3].router._links[link]
        unreachable = machine.unreachable_outgoing_chips()
        self.assertListEqual([(3, 3)], unreachable)

    def test_unreachable_incoming_local_chips(self):
        set_config("Machine", "version", 5)
        down_chips = [(8, 6), (9, 7), (9, 8)]
        down_str = ":".join([f"{x},{y}" for x, y in down_chips])
        set_config("Machine", "down_chips", down_str)
        machine = virtual_machine(16, 16)
        unreachable = machine.unreachable_incoming_local_chips()
        self.assertListEqual([(8, 7)], unreachable)

    def test_unreachable_outgoing_local_chips(self):
        set_config("Machine", "version", 5)
        down_chips = [(8, 6), (9, 7), (9, 8)]
        down_str = ":".join([f"{x},{y}" for x, y in down_chips])
        set_config("Machine", "down_chips", down_str)
        machine = virtual_machine(16, 16)
        unreachable = machine.unreachable_outgoing_local_chips()
        self.assertListEqual([(8, 7)], unreachable)

    def test_repair_with_local_orphan(self):
        set_config("Machine", "version", 5)
        down_chips = [(8, 6), (9, 7), (9, 8)]
        down_str = ":".join([f"{x},{y}" for x, y in down_chips])
        set_config("Machine", "down_chips", down_str)
        machine = virtual_machine(16, 16)
        with self.assertRaises(SpinnMachineException):
            set_config("Machine", "repair_machine", False)
            repaired = machine_repair(machine)
        set_config("Machine", "repair_machine", True)
        repaired = machine_repair(machine)
        self.assertTrue(machine.is_chip_at(8, 7))
        self.assertFalse(repaired.is_chip_at(8, 7))

    def test_repair_with_one_way_links_different_boards(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(12, 12)
        # Delete some links between boards
        down_links = [
            (7, 7, 0), (7, 3, 1), (6, 7, 2), (4, 7, 3), (8, 6, 4), (8, 4, 5)]
        for (x, y, link) in down_links:
            del machine._chips[x, y].router._links[link]
        with self.assertRaises(SpinnMachineException):
            set_config("Machine", "repair_machine", False)
            new_machine = machine_repair(machine)
        set_config("Machine", "repair_machine", True)
        new_machine = machine_repair(machine)
        self.assertIsNotNone(new_machine)

    def test_oneway_link_no_repair(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(8, 8)

        # Delete some random links
        down_links = [
            (3, 6, 0), (5, 4, 1), (3, 2, 5), (1, 3, 3)]
        for (x, y, link) in down_links:
            if machine.is_link_at(x, y, link):
                del machine._chips[x, y].router._links[link]
        with self.assertRaises(SpinnMachineException):
            set_config("Machine", "repair_machine", False)
            new_machine = machine_repair(machine)
        set_config("Machine", "repair_machine", True)
        new_machine = machine_repair(machine)
        self.assertIsNotNone(new_machine)

    def test_removed_chip_repair(self):
        set_config("Machine", "version", 5)
        machine = virtual_machine(8, 8)

        del machine._chips[(3, 3)]
        set_config("Machine", "repair_machine", False)
        new_machine = machine_repair(machine, [(3, 3)])
        self.assertIsNotNone(new_machine)
        self.assertFalse(new_machine.is_link_at(2, 2, 1))

    def test_ignores(self):
        set_config("Machine", "version", 5)
        set_config("Machine", "down_chips", "2,2:4,4:6,6,ignored_ip")
        set_config("Machine", "down_cores",
                   "1,1,1:3,3,3: 5,5,-5:7,7,7,ignored_ip:0,0,5-10")
        set_config("Machine", "down_links", "1,3,3:3,5,3:5,3,3,ignored_ip")

        machine = virtual_machine(8, 8)

        self.assertFalse(machine.is_chip_at(4, 4))
        self.assertFalse(machine.is_chip_at(2, 2))
        self.assertTrue(machine.is_chip_at(6, 6))
        self.assertTrue(machine.is_chip_at(0, 0))

        chip = machine.get_chip_at(3, 3)
        self.assertFalse(chip.is_processor_with_id(3))

        chip = machine.get_chip_at(5, 5)
        self.assertFalse(chip.is_processor_with_id(6))

        chip = machine.get_chip_at(7, 7)
        self.assertTrue(chip.is_processor_with_id(6))

        chip = machine.get_chip_at(1, 1)
        self.assertFalse(chip.is_processor_with_id(1))

        router = machine.get_chip_at(1, 3).router
        self.assertFalse(router.is_link(3))

        router = machine.get_chip_at(3, 5).router
        self.assertFalse(router.is_link(3))

        router = machine.get_chip_at(5, 3).router
        self.assertTrue(router.is_link(3))

        chip = machine.get_chip_at(0, 0)
        for i in range(0, 5):
            self.assertTrue(chip.is_processor_with_id(i))
        for i in range(5, 11):
            self.assertFalse(chip.is_processor_with_id(i))
        for i in range(12, 18):
            self.assertTrue(chip.is_processor_with_id(i))

    def test_bad_ignores(self):
        try:
            IgnoreChip.parse_string("4,4,3,4:6,6,ignored_ip")
        except Exception as ex:
            self.assertTrue("downed_chip" in str(ex))

        try:
            IgnoreCore.parse_string("3,3,3,4: 5,5,-5:7,7,7,ignored_ip")
        except Exception as ex:
            self.assertTrue("downed_core" in str(ex))

        empty = IgnoreCore.parse_string(None)
        self.assertEqual(len(empty), 0)

        try:
            IgnoreLink.parse_string("1,3:5,3,3,ignored_ip")
        except Exception as ex:
            self.assertTrue("downed_link" in str(ex))

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
        chip1112 = machine.get_chip_at(11, 12)
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

    def test_n_cores_2_2(self):
        set_config("Machine", "version", 2)
        machine = virtual_machine(2, 2)
        n_cores = sum(
            cores for (_, cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, 4 * 18)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, 4 * 18)


if __name__ == '__main__':
    unittest.main()
