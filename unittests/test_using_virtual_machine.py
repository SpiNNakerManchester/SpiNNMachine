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

from parameterized import parameterized
from typing import Tuple
import unittest

from spinn_utilities.config_holder import set_config
from spinn_utilities.typing.coords import XY

from spinn_machine.config_setup import unittest_setup
from spinn_machine import virtual_machine
from spinn_machine.virtual_machine import (
    virtual_machine_by_boards, virtual_machine_by_min_size)
from spinn_machine.data import MachineDataView
from spinn_machine.exceptions import (SpinnMachineException)
from spinn_machine.machine_factory import machine_repair
from spinn_machine.version import (
    ALL_BOARD_TYPES, BIG_BOARD_TYPES, FOUR_PLUS_BOARD_TYPES)
from .geometry import (to_xyz, shortest_mesh_path_length,
                       shortest_torus_path_length, minimise_xyz)


class TestUsingVirtualMachine(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    @parameterized.expand(ALL_BOARD_TYPES)
    def test_new_vm_with_max_cores(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        version = MachineDataView.get_machine_version()
        n_cpus = version.max_cores_per_chip - 5
        set_config("Machine", "max_machine_core", str(n_cpus))
        # HACK Unsupported! Need new the version again after the cfg changed
        data = (MachineDataView.
                _MachineDataView__data)    # type: ignore[attr-defined]
        data._machine_version = None
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

    @parameterized.expand(ALL_BOARD_TYPES)
    def test_iter_chips(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        vm = virtual_machine_by_boards(1)
        n_chips = MachineDataView.get_machine_version().n_chips_per_board
        self.assertEqual(n_chips, vm.n_chips)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(n_chips, count)

    @parameterized.expand(FOUR_PLUS_BOARD_TYPES)
    def test_down_chip(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
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

    def _check_path(self, source: XY, target: XY, path: Tuple[int, int, int],
                    width: int, height: int) -> None:
        new_target = ((source[0] + path[0] - path[2]) % width,
                      (source[1] + path[1] - path[2]) % height)
        self.assertEqual(target, new_target, "{}{}".format(source, path))

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_nowrap_shortest_path(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
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

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_fullwrap_shortest_path(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
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

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_hoizontal_wrap_shortest_path(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
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

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_vertical_wrap_shortest_path(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
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

    @parameterized.expand(ALL_BOARD_TYPES)
    def test_minimize(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        machine = virtual_machine_by_boards(1)
        for x in range(-3, 3):
            for y in range(-3, 3):
                min1 = minimise_xyz((x, y, 0))
                min2 = machine._minimize_vector(x, y)
                self.assertEqual(min1, min2)

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_unreachable_incoming_chips(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        machine = virtual_machine_by_min_size(6, 6)

        # Delete links incoming to 3, 3
        down_links = [
            (2, 2, 1), (2, 3, 0), (3, 4, 5), (4, 4, 4), (4, 3, 3), (3, 2, 2)]
        for (x, y, link) in down_links:
            if machine.is_link_at(x, y, link):
                del machine._chips[x, y].router._links[link]
        unreachable = machine.unreachable_incoming_chips()
        self.assertListEqual([(3, 3)], unreachable)

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_unreachable_outgoing_chips(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        machine = virtual_machine_by_min_size(6, 6)

        # Delete links outgoing from 3, 3
        for link in range(6):
            if machine.is_link_at(3, 3, link):
                del machine._chips[3, 3].router._links[link]
        unreachable = machine.unreachable_outgoing_chips()
        self.assertListEqual([(3, 3)], unreachable)

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_unreachable_incoming_local_chips(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        # Assumes boards of exactly size 8,8
        down_chips = [(8, 6), (9, 7), (9, 8)]
        down_str = ":".join([f"{x},{y}" for x, y in down_chips])
        set_config("Machine", "down_chips", down_str)
        machine = virtual_machine(16, 16)
        unreachable = machine.unreachable_incoming_local_chips()
        self.assertListEqual([(8, 7)], unreachable)

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_unreachable_outgoing_local_chips(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        # Assumes boards of exactly size 8,8
        down_chips = [(8, 6), (9, 7), (9, 8)]
        down_str = ":".join([f"{x},{y}" for x, y in down_chips])
        set_config("Machine", "down_chips", down_str)
        machine = virtual_machine(16, 16)
        unreachable = machine.unreachable_outgoing_local_chips()
        self.assertListEqual([(8, 7)], unreachable)

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_repair_with_local_orphan(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        # Assumes boards of exactly size 8,8
        down_chips = [(8, 6), (9, 7), (9, 8)]
        down_str = ":".join([f"{x},{y}" for x, y in down_chips])
        set_config("Machine", "down_chips", down_str)
        machine = virtual_machine(16, 16)
        with self.assertRaises(SpinnMachineException):
            set_config("Machine", "repair_machine", "False")
            repaired = machine_repair(machine)
        set_config("Machine", "repair_machine", "True")
        repaired = machine_repair(machine)
        self.assertTrue(machine.is_chip_at(8, 7))
        self.assertFalse(repaired.is_chip_at(8, 7))

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_repair_with_one_way_links_different_boards(
            self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        machine = virtual_machine(12, 12)
        # Assumes boards of exactly size 8,8
        # Delete some links between boards
        down_links = [
            (7, 7, 0), (7, 3, 1), (6, 7, 2), (4, 7, 3), (8, 6, 4), (8, 4, 5)]
        for (x, y, link) in down_links:
            del machine._chips[x, y].router._links[link]
        with self.assertRaises(SpinnMachineException):
            set_config("Machine", "repair_machine", "False")
            new_machine = machine_repair(machine)
        set_config("Machine", "repair_machine", "True")
        new_machine = machine_repair(machine)
        self.assertIsNotNone(new_machine)

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_oneway_link_no_repair(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        machine = virtual_machine(8, 8)

        # Delete some random links
        down_links = [
            (3, 6, 0), (5, 4, 1), (3, 2, 5), (1, 3, 3)]
        for (x, y, link) in down_links:
            if machine.is_link_at(x, y, link):
                del machine._chips[x, y].router._links[link]
        with self.assertRaises(SpinnMachineException):
            set_config("Machine", "repair_machine", "False")
            new_machine = machine_repair(machine)
        set_config("Machine", "repair_machine", "True")
        new_machine = machine_repair(machine)
        self.assertIsNotNone(new_machine)

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_removed_chip_repair(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        machine = virtual_machine_by_boards(1)

        del machine._chips[(3, 3)]
        set_config("Machine", "repair_machine", "False")
        new_machine = machine_repair(machine, [(3, 3)])
        self.assertIsNotNone(new_machine)
        self.assertFalse(new_machine.is_link_at(2, 2, 1))

    @parameterized.expand(BIG_BOARD_TYPES)
    def test_ignores(self, _: str, ver_num: str) -> None:
        set_config("Machine", "version", ver_num)
        set_config("Machine", "down_chips", "2,2:4,4:6,6,ignored_ip")
        set_config("Machine", "down_cores",
                   "1,1,4:3,3,3: 5,5,-5:7,7,7,ignored_ip:0,0,5-10")
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
        self.assertFalse(chip.is_processor_with_id(4))

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
