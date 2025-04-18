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

from spinn_machine import Chip, Link, Router, virtual_machine
from spinn_machine.config_setup import unittest_setup
from spinn_machine.data import MachineDataView
from spinn_machine.exceptions import (
    SpinnMachineException, SpinnMachineAlreadyExistsException)
from spinn_machine.version import SPIN2_1CHIP
from spinn_machine.virtual_machine import (
    virtual_machine_by_boards, virtual_machine_by_chips,
    virtual_machine_by_cores)


class TestVirtualMachine201(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def _create_chip(self, x: int, y: int) -> Chip:
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
            return Chip(x, y, [0], range(1, n_processors), _router, _sdram,
                        nearest_ethernet_chip[0],
                        nearest_ethernet_chip[1], _ip)
        else:
            return Chip(x, y, [0], range(1, n_processors), _router, _sdram,
                        nearest_ethernet_chip[0],
                        nearest_ethernet_chip[1], None)

    def test_illegal_vms(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=-1, height=2)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=2, height=-1)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=15, height=15)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=8, height=8)
        with self.assertRaises(SpinnMachineException):
            virtual_machine(width=2, height=2)

    def test_version_SPIN2_1CHIP(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        vm = virtual_machine(width=1, height=1)
        self.assertEqual(1, vm.n_chips)
        self.assertTrue(vm.is_chip_at(0, 0))
        self.assertFalse(vm.is_chip_at(0, 1))
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertFalse(vm.is_link_at(0, 0, 0))
        self.assertFalse(vm.is_link_at(0, 0, 1))
        self.assertFalse(vm.is_link_at(0, 0, 2))
        self.assertFalse(vm.is_link_at(0, 0, 3))
        self.assertFalse(vm.is_link_at(0, 0, 4))
        self.assertFalse(vm.is_link_at(0, 0, 5))

        count = 0
        for _chip in vm.chips:
            for _link in _chip.router.links:
                count += 1
        self.assertEqual(0, count)
        self.assertEqual(153, vm.get_cores_count())
        self.assertEqual(0, vm.get_links_count())
        count = 0
        for _xy in vm.get_existing_xys_on_board(vm[0, 0]):
            count += 1
        self.assertEqual(1, count)
        self.assertEqual((1, 0), vm.get_unused_xy())
        self.assertEqual(0, len(list(vm.spinnaker_links)))
        self.assertEqual(0, len(vm._fpga_links))

    def test_new_vm_with_max_cores(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        n_cpus = 105
        set_config("Machine", "max_machine_core", str(n_cpus))
        vm = virtual_machine(1, 1, validate=True)
        _chip = vm[0, 0]
        self.assertEqual(n_cpus, _chip.n_processors)
        self.assertEqual(n_cpus - 1, _chip.n_placable_processors)
        self.assertEqual(1, _chip.n_scamp_processors)
        self.assertEqual(n_cpus - 1, len(list(_chip.placable_processors_ids)))
        self.assertEqual(1, len(list(_chip.scamp_processors_ids)))
        count = sum(_chip.n_processors for _chip in vm.chips)
        self.assertEqual(count, 1 * n_cpus)

    def test_iter_chips(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        vm = virtual_machine(1, 1)
        self.assertEqual(1, vm.n_chips)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(1, count)

    def test_add_existing_chip(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        vm = virtual_machine(1, 1)
        _chip = self._create_chip(0, 0)
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            vm.add_chip(_chip)

    def test_chips(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        vm = virtual_machine(1, 1)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(count, 1)

    def test_ethernet_chips_exist(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        vm = virtual_machine(width=1, height=1)
        for eth_chip in vm._ethernet_connected_chips:
            self.assertTrue(vm.get_chip_at(eth_chip.x, eth_chip.y),
                            "Eth chip location x={}, y={} not in "
                            "_configured_chips"
                            .format(eth_chip.x, eth_chip.y))

    def test_boot_chip(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        vm = virtual_machine(1, 1)
        # as Chip == its XY
        self.assertEqual(vm.boot_chip, (0, 0))

    def test_get_chips_on_boards(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        vm = virtual_machine(width=1, height=1)
        # check each chip appears only once on the entire board
        count00 = 0
        count01 = 0
        count04 = 0
        for eth_chip in vm._ethernet_connected_chips:
            list_of_chips = list(vm.get_existing_xys_on_board(eth_chip))
            self.assertEqual(len(list_of_chips), 1)
            if (0, 0) in list_of_chips:
                count00 += 1
            if (0, 1) in list_of_chips:
                count01 += 1
            if (0, 4) in list_of_chips:
                count04 += 1
        # (0,0) is on this virtual machine
        self.assertEqual(count00, 1)

        # (0, 1), (24,36) is not on this virtual machine
        self.assertEqual(count01, 0)
        self.assertEqual(count04, 0)

    def test_fpga_links_single_board(self) -> None:
        set_config("Machine", "version", "3")
        machine = virtual_machine(width=2, height=2)
        machine.add_fpga_links()
        self.assertEqual(0, len(machine._fpga_links))

    def test_size_2_2(self) -> None:
        set_config("Machine", "version", "2")
        machine = virtual_machine(2, 2, validate=True)
        ethernet = machine[0, 0]
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
        self.assertEqual(4, len(list(machine.local_xys)))

    def test_size_2_2_hole(self) -> None:
        set_config("Machine", "version", "2")
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

    def test_n_cores_2_2(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        machine = virtual_machine(1, 1)
        n_cores = sum(
            cores for (_, cores) in machine.get_xy_cores_by_ethernet(0, 0))
        self.assertEqual(n_cores, 153)
        n_cores = sum(chip.n_processors for chip in machine.chips)
        self.assertEqual(n_cores, 153)

    def test_by(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        n_cores = 40
        machine = virtual_machine_by_cores(n_cores)
        self.assertEqual(1, machine.n_chips)
        self.assertEqual(1, machine.width)
        self.assertEqual(1, machine.height)
        self.assertGreaterEqual(machine.total_available_user_cores, n_cores)
        machine2 = virtual_machine_by_boards(1)
        self.assertEqual(1, machine2.n_chips)
        self.assertEqual(1, machine2.width)
        self.assertEqual(1, machine2.height)
        machine = virtual_machine_by_chips(1)
        self.assertEqual(1, machine.n_chips)
        self.assertEqual(1, machine.width)
        self.assertEqual(1, machine.height)

    def test_by_cores_too_many(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        with self.assertRaises(SpinnMachineException):
            virtual_machine_by_cores(200)
        with self.assertRaises(SpinnMachineException):
            virtual_machine_by_boards(2)

    def test_down(self) -> None:
        set_config("Machine", "version", str(SPIN2_1CHIP))
        set_config("Machine", "down_cores", "0,0,2.2.1")
        version = MachineDataView.get_machine_version()
        self.assertEqual(90, version.qx_qy_qp_to_id(2, 2, 1))

        machine = virtual_machine_by_cores(1)
        chip = machine[(0, 0)]
        self.assertFalse(chip.is_processor_with_id(90))


if __name__ == '__main__':
    unittest.main()
