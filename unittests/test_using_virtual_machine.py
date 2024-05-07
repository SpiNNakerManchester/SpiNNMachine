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
from spinn_machine.virtual_machine import (
    virtual_machine_by_boards, virtual_machine_by_min_size)
from spinn_machine.data import MachineDataView
from spinn_machine.exceptions import (SpinnMachineException)
from spinn_machine.ignores import IgnoreChip, IgnoreCore, IgnoreLink
from spinn_machine.machine_factory import machine_repair
from spinn_machine.version.version_strings import VersionStrings
from spinn_machine.version.version_5 import CHIPS_PER_BOARD
from .geometry import (to_xyz, shortest_mesh_path_length,
                       shortest_torus_path_length, minimise_xyz)


class TestUsingVirtualMachine(unittest.TestCase):

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

    def test_new_vm_with_max_cores(self):
        set_config("Machine", "versions", VersionStrings.ANY.text)
        version = MachineDataView.get_machine_version()
        n_cpus = version.max_cores_per_chip - 5
        set_config("Machine", "max_machine_core", n_cpus)
        # HACK Unsupported! Need new the version again after the cfg changed
        MachineDataView._MachineDataView__data._machine_version = None
        version = MachineDataView.get_machine_version()
        vm = virtual_machine_by_boards(1, validate=True)
        for chip in vm.chips:
            self.assertEqual(n_cpus, chip.n_processors)
            self.assertEqual(n_cpus - version.n_scamp_cores,
                             chip.n_placable_processors)
            self.assertEqual(version.n_scamp_cores, chip.n_scamp_processors)
            self.assertEqual(n_cpus - version.n_scamp_cores,
                             len(list(chip.placable_processors_ids)))
            self.assertEqual(version.n_scamp_cores,
                             len(list(chip.scamp_processors_ids)))

    def test_iter_chips(self):
        set_config("Machine", "versions", VersionStrings.ANY.text)
        vm = virtual_machine_by_boards(1)
        n_chips = MachineDataView.get_machine_version().n_chips_per_board
        self.assertEqual(n_chips, vm.n_chips)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(n_chips, count)

    def test_down_chip(self):
        set_config("Machine", "versions", VersionStrings.FOUR_PLUS.text)
        down_chips = set()
        down_chips.add((1, 1))
        set_config("Machine", "down_chips", "1,1")
        vm = virtual_machine_by_boards(1)
        n_chips = MachineDataView.get_machine_version().n_chips_per_board
        self.assertEqual(n_chips - 1, vm.n_chips)
        count = 0
        for _chip in vm.chip_coordinates:
            count += 1
            self.assertNotIn(_chip, down_chips)
        self.assertEqual(n_chips - 1, count)

    def _check_path(self, source, target, path, width, height):
        new_target = ((source[0] + path[0] - path[2]) % width,
                      (source[1] + path[1] - path[2]) % height)
        self.assertEqual(target, new_target, "{}{}".format(source, path))

    def test_nowrap_shortest_path(self):
        set_config("Machine", "versions", VersionStrings.EIGHT_BY_EIGHT.text)
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
        set_config("Machine", "versions", VersionStrings.EIGHT_BY_EIGHT.text)
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
        set_config("Machine", "versions", VersionStrings.EIGHT_BY_EIGHT.text)
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
        set_config("Machine", "versions", VersionStrings.EIGHT_BY_EIGHT.text)
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
        set_config("Machine", "versions", VersionStrings.ANY.text)
        machine = virtual_machine_by_boards(1)
        for x in range(-3, 3):
            for y in range(-3, 3):
                min1 = minimise_xyz((x, y, 0))
                min2 = machine._minimize_vector(x, y)
                self.assertEqual(min1, min2)

    def test_unreachable_incoming_chips(self):
        set_config("Machine", "versions", VersionStrings.BIG.text)
        machine = virtual_machine_by_min_size(6, 6)

        # Delete links incoming to 3, 3
        down_links = [
            (2, 2, 1), (2, 3, 0), (3, 4, 5), (4, 4, 4), (4, 3, 3), (3, 2, 2)]
        for (x, y, link) in down_links:
            if machine.is_link_at(x, y, link):
                del machine._chips[x, y].router._links[link]
        unreachable = machine.unreachable_incoming_chips()
        self.assertListEqual([(3, 3)], unreachable)

    def test_unreachable_outgoing_chips(self):
        set_config("Machine", "versions", VersionStrings.BIG.text)
        machine = virtual_machine_by_min_size(6, 6)

        # Delete links outgoing from 3, 3
        for link in range(6):
            if machine.is_link_at(3, 3, link):
                del machine._chips[3, 3].router._links[link]
        unreachable = machine.unreachable_outgoing_chips()
        self.assertListEqual([(3, 3)], unreachable)

    def test_unreachable_incoming_local_chips(self):
        set_config("Machine", "versions", VersionStrings.EIGHT_BY_EIGHT.text)
        # Assumes boards of exactly size 8,8
        down_chips = [(8, 6), (9, 7), (9, 8)]
        down_str = ":".join([f"{x},{y}" for x, y in down_chips])
        set_config("Machine", "down_chips", down_str)
        machine = virtual_machine(16, 16)
        unreachable = machine.unreachable_incoming_local_chips()
        self.assertListEqual([(8, 7)], unreachable)

    def test_unreachable_outgoing_local_chips(self):
        set_config("Machine", "versions", VersionStrings.EIGHT_BY_EIGHT.text)
        # Assumes boards of exactly size 8,8
        down_chips = [(8, 6), (9, 7), (9, 8)]
        down_str = ":".join([f"{x},{y}" for x, y in down_chips])
        set_config("Machine", "down_chips", down_str)
        machine = virtual_machine(16, 16)
        unreachable = machine.unreachable_outgoing_local_chips()
        self.assertListEqual([(8, 7)], unreachable)

    def test_repair_with_local_orphan(self):
        set_config("Machine", "versions", VersionStrings.EIGHT_BY_EIGHT.text)
        # Assumes boards of exactly size 8,8
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
        set_config("Machine", "versions", VersionStrings.EIGHT_BY_EIGHT.text)
        machine = virtual_machine(12, 12)
        # Assumes boards of exactly size 8,8
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
        set_config("Machine", "versions", VersionStrings.EIGHT_BY_EIGHT.text)
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
        set_config("Machine", "versions", VersionStrings.BIG.text)
        machine = virtual_machine_by_boards(1)

        del machine._chips[(3, 3)]
        set_config("Machine", "repair_machine", False)
        new_machine = machine_repair(machine, [(3, 3)])
        self.assertIsNotNone(new_machine)
        self.assertFalse(new_machine.is_link_at(2, 2, 1))

    def test_ignores(self):
        set_config("Machine", "versions", VersionStrings.BIG.text)
        set_config("Machine", "down_chips", "2,2:4,4:6,6,ignored_ip")
        set_config("Machine", "down_cores",
                   "1,1,1:3,3,3: 5,5,-5:7,7,7,ignored_ip:0,0,5-10")
        set_config("Machine", "down_links", "1,3,3:3,5,3:5,3,3,ignored_ip")

        machine = virtual_machine_by_min_size(8, 8)

        self.assertFalse(machine.is_chip_at(4, 4))
        self.assertFalse(machine.is_chip_at(2, 2))
        self.assertTrue(machine.is_chip_at(6, 6))
        self.assertTrue(machine.is_chip_at(0, 0))

        chip = machine[3, 3]
        self.assertFalse(chip.is_processor_with_id(3))

        chip = machine[5, 5]
        self.assertFalse(chip.is_processor_with_id(6))

        chip = machine[7, 7]
        self.assertTrue(chip.is_processor_with_id(6))

        chip = machine[1, 1]
        self.assertFalse(chip.is_processor_with_id(1))

        router = machine[1, 3].router
        self.assertFalse(router.is_link(3))

        router = machine[3, 5].router
        self.assertFalse(router.is_link(3))

        router = machine[5, 3].router
        self.assertTrue(router.is_link(3))

        chip = machine[0, 0]
        for i in range(0, 5):
            self.assertTrue(chip.is_processor_with_id(i))
        for i in range(5, 11):
            self.assertFalse(chip.is_processor_with_id(i))
        for i in range(12, 18):
            self.assertTrue(chip.is_processor_with_id(i))


if __name__ == '__main__':
    unittest.main()
