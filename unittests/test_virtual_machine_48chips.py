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
from spinn_machine.version.version_strings import VersionStrings
from spinn_machine.virtual_machine import (
    virtual_machine_by_boards, virtual_machine_by_chips,
    virtual_machine_by_cores, virtual_machine_by_min_size)


class TestVirtualMachine48Chips(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_illegal_vms(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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
        with self.assertRaises(SpinnMachineException):
            virtual_machine(size_x, None,  # type: ignore[arg-type]
                            validate=True)

    def test_version_hole(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_version_hole2(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_12_n_plus4_12_m_4(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        size_x = 12 * 5
        size_y = 12 * 7
        vm = virtual_machine(size_x + 4, size_y + 4, validate=True)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_12_n_12_m(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        size_x = 12 * 5
        size_y = 12 * 7
        vm = virtual_machine(size_x, size_y, validate=True)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_chips(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        vm = virtual_machine(8, 8)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(count, 48)

    def test_ethernet_chips_exist(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        vm = virtual_machine(width=48, height=24)
        for eth_chip in vm._ethernet_connected_chips:
            self.assertTrue(vm.get_chip_at(eth_chip.x, eth_chip.y),
                            "Eth chip location x={}, y={} not in "
                            "_configured_chips"
                            .format(eth_chip.x, eth_chip.y))

    def test_boot_chip(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        vm = virtual_machine(12, 12)
        # based on Chip equaling its XY
        self.assertEqual(vm.boot_chip, (0, 0))

    def test_get_chips_on_boards(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_big(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        virtual_machine(
            width=240, height=240, validate=True)

    def test_48_28(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_48_24(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_52_28(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_52_24(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_fullwrap_holes(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_horizontal_wrap_holes(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_vertical_wrap_holes(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_no_wrap_holes(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_n_cores_full_wrap(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        version = MachineDataView.get_machine_version()
        cores_per_board = sum(version.chip_core_map.values())
        machine = virtual_machine(12, 12)
        n_cores = sum(
            n_cores
            for (_, n_cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, cores_per_board)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, cores_per_board * 3)

    def test_n_cores_no_wrap(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        version = MachineDataView.get_machine_version()
        cores_per_board = sum(version.chip_core_map.values())
        machine = virtual_machine(16, 16)
        n_cores = sum(
            n_cores
            for (_, n_cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, cores_per_board)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, cores_per_board * 3)
        chip34 = machine.get_chip_at(3, 4)
        assert chip34 is not None
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

    def test_n_cores_horizontal_wrap(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        version = MachineDataView.get_machine_version()
        cores_per_board = sum(version.chip_core_map.values())
        machine = virtual_machine(12, 16)
        n_cores = sum(
            n_cores
            for (_, n_cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, cores_per_board)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, cores_per_board * 3)

    def test_n_cores_vertical_wrap(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        version = MachineDataView.get_machine_version()
        cores_per_board = sum(version.chip_core_map.values())
        machine = virtual_machine(12, 16)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, cores_per_board * 3)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, cores_per_board * 3)

    def test_n_cores_8_8(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        version = MachineDataView.get_machine_version()
        cores_per_board = sum(version.chip_core_map.values())
        machine = virtual_machine(8, 8)
        n_cores = sum(
            cores for (_, cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, cores_per_board)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, cores_per_board)

    def test_8_8_by_cores_1_board(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_8_8_by_cores_3_boards(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_8_8_by_cores_6_boards(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_8_8_by_cores_12_boards(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_8_8_by_cores_18_boards(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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

    def test_by_min_size(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        machine = virtual_machine_by_min_size(15, 21)
        self.assertGreaterEqual(machine.width, 15)
        self.assertGreaterEqual(machine.height, 21)

    def test_by_min_size_edge_case(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
        version = MachineDataView.get_machine_version()
        width, height = version.board_shape
        machine = virtual_machine_by_min_size(width, height + 1)
        self.assertGreaterEqual(machine.width, width)
        self.assertGreaterEqual(machine.height, height + 1)


if __name__ == '__main__':
    unittest.main()
