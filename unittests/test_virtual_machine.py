import unittest
from spinn_machine import Processor, Link, SDRAM, Router, Chip, virtual_machine
from spinn_machine.exceptions import (
    SpinnMachineException, SpinnMachineAlreadyExistsException,
    SpinnMachineInvalidParameterException)
from spinn_machine.machine_factory import machine_repair
from .geometry import (to_xyz, shortest_mesh_path_length,
                       shortest_torus_path_length, minimise_xyz)


class TestVirtualMachine(unittest.TestCase):

    def _create_chip(self, x, y):
        # Create a list of processors.

        flops = 1000
        processors = list()
        for i in range(18):
            processors.append(Processor(i, flops, is_monitor=(i == 0)))

        links = list()
        links.append(Link(0, 0, 0, 1, 1))
        links.append(Link(0, 1, 1, 1, 0))
        links.append(Link(1, 1, 2, 0, 0))
        links.append(Link(1, 0, 3, 0, 1))
        _router = Router(links, False, 100, 1024)

        _sdram = SDRAM(128)
        nearest_ethernet_chip = (0, 0)
        _ip = "192.162.240.253"

        if (x == y == 0):
            return Chip(x, y, processors, _router, _sdram,
                        nearest_ethernet_chip[0],
                        nearest_ethernet_chip[1], _ip)
        else:
            return Chip(x, y, processors, _router, _sdram,
                        nearest_ethernet_chip[0],
                        nearest_ethernet_chip[1], None)

    def test_illegal_vms(self):
        with self.assertRaises(SpinnMachineInvalidParameterException):
            virtual_machine(width=-1, height=2)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            virtual_machine(width=2, height=-1)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            virtual_machine(version=0)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            virtual_machine(version=3, with_wrap_arounds=True)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            virtual_machine(version=3, width=12, height=12)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            virtual_machine(version=5, with_wrap_arounds=True)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            virtual_machine(version=5, width=12, height=12)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            virtual_machine(with_wrap_arounds=True, width=15, height=15)

    def test_version_2(self):
        vm = virtual_machine(version=2, with_wrap_arounds=None)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
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
        self.assertEqual(vm.get_cores_and_link_count(), (72, 8))
        count = 0
        for _chip in vm.get_existing_xys_on_board(vm.get_chip_at(1, 1)):
            count += 1
        self.assertEqual(4, count)

    def test_2_with_wrapparound(self):
        vm = virtual_machine(
            height=2, width=2, with_wrap_arounds=True, validate=True)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEqual(4, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertTrue(vm.is_link_at(0, 0, 5))
        self.assertTrue(vm.is_link_at(0, 1, 2))
        self.assertTrue(vm.is_link_at(0, 0, 4))
        self.assertTrue(vm.is_link_at(0, 1, 3))

        # Test that the chip south of 0, 0 is 0, 1 (with wrap around)
        chip = vm.get_chip_at(0, 0)
        link = chip.router.get_link(5)
        self.assertEqual(link.destination_x, 0)
        self.assertEqual(link.destination_y, 1)

        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(24, count)

    def test_2_no_wrapparound(self):
        vm = virtual_machine(
            height=2, width=2, with_wrap_arounds=False, validate=True)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEqual(4, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertFalse(vm.is_link_at(0, 0, 5))
        self.assertFalse(vm.is_link_at(0, 1, 2))
        self.assertFalse(vm.is_link_at(0, 0, 4))
        self.assertFalse(vm.is_link_at(0, 1, 3))
        count = 0
        for _chip in vm.chips:
            for _link in _chip.router.links:
                count += 1
        self.assertEqual(10, count)

    def test_version_5(self):
        vm = virtual_machine(version=5, validate=True)
        self.assertEqual(vm.max_chip_x, 7)
        self.assertEqual(vm.max_chip_y, 7)
        self.assertEqual(48, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertTrue(vm.is_chip_at(4, 4))
        self.assertFalse(vm.is_chip_at(0, 4))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(240, count)

    def test_8_by_8(self):
        vm = virtual_machine(width=8, height=8, version=None,
                             with_wrap_arounds=False, validate=True)
        self.assertEqual(vm.max_chip_x, 7)
        self.assertEqual(vm.max_chip_y, 7)
        self.assertEqual(48, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertTrue(vm.is_chip_at(4, 4))
        self.assertFalse(vm.is_chip_at(0, 4))
        self.assertFalse((0, 4) in list(vm.chip_coordinates))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(240, count)

    def test_version_5_guess_12x12(self):
        vm = virtual_machine(height=12, width=12, version=None,
                             with_wrap_arounds=None, validate=True)
        self.assertEqual(vm.max_chip_x, 11)
        self.assertEqual(vm.max_chip_y, 11)
        self.assertEqual(144, vm.n_chips)
        self.assertEqual(3, len(vm.ethernet_connected_chips))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(864, count)
        count = 0
        for _chip in vm.get_existing_xys_on_board(vm.get_chip_at(1, 1)):
            count += 1
        self.assertEqual(48, count)

    def test_version_5_guess_8x8(self):
        vm = virtual_machine(height=8, width=8, version=None,
                             with_wrap_arounds=None, validate=True)
        self.assertEqual(vm.max_chip_x, 7)
        self.assertEqual(vm.max_chip_y, 7)
        self.assertEqual(48, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(240, count)

    def test_version_5_hole(self):
        hole = [(3, 3)]
        vm = virtual_machine(version=5, down_chips=hole, validate=True)
        self.assertEqual(vm.max_chip_x, 7)
        self.assertEqual(vm.max_chip_y, 7)
        self.assertEqual(47, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertFalse(vm.is_link_at(3, 3, 2))
        self.assertFalse(vm.is_link_at(3, 2, 2))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(228, count)
        self.assertEqual(48, len(vm.local_xys))

    def test_new_vm_no_monitor(self):
        n_cpus = 11
        vm = virtual_machine(
            2, 2, n_cpus_per_chip=n_cpus, with_monitors=False, validate=True)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEqual(n_cpus, vm.maximum_user_cores_on_chip)
        _chip = vm.get_chip_at(1, 1)
        self.assertEqual(n_cpus, _chip.n_processors)
        monitors = 0
        normal = 0
        for core in _chip.processors:
            if core.is_monitor:
                monitors += 1
            else:
                normal += 1
        self.assertEqual(n_cpus, normal)
        self.assertEqual(0, monitors)

    def test_new_vm_with_monitor(self):
        n_cpus = 13
        vm = virtual_machine(
            2, 2, n_cpus_per_chip=n_cpus, with_monitors=True, validate=True)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEqual(n_cpus - 1, vm.maximum_user_cores_on_chip)
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
        vm = virtual_machine(2, 2)
        self.assertEqual(4, vm.n_chips)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertTrue(4, count)

    def test_down_chip(self):
        down_chips = set()
        down_chips.add((1, 1))
        vm = virtual_machine(2, 2, down_chips=down_chips)
        self.assertEqual(3, vm.n_chips)
        count = 0
        for _chip in vm.chip_coordinates:
            count += 1
            self.assertNotIn(_chip, down_chips)
        self.assertTrue(3, count)

    def test_add_existing_chip(self):
        vm = virtual_machine(2, 2)
        _chip = self._create_chip(1, 1)
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            vm.add_chip(_chip)

    def test_weird_size(self):
        with self.assertRaises(SpinnMachineInvalidParameterException):
            virtual_machine(5, 7)

    def test_12_n_plus4_12_m_4(self):
        size_x = 12 * 5
        size_y = 12 * 7
        vm = virtual_machine(size_x + 4, size_y + 4, validate=True)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_12_n_12_m(self):
        size_x = 12 * 5
        size_y = 12 * 7
        vm = virtual_machine(size_x, size_y, with_wrap_arounds=True,
                             validate=True)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_add__chip(self):
        vm = virtual_machine(2, 2)

        _chip = self._create_chip(2, 2)
        _chip._virtual = True
        vm.add_chip(_chip)
        self.assertEqual(vm.max_chip_x, 2)
        self.assertEqual(vm.max_chip_y, 2)
        self.assertEqual(5, vm.n_chips)

        self.assertTrue(vm.is_chip_at(2, 2))
        _good = vm.get_chip_at(2, 2)
        self.assertEqual(_chip, _good)

        _bad = vm.get_chip_at(2, 1)
        self.assertIsNone(_bad)

        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertTrue(5, count)

    def test_add_high_chip_with_down(self):
        down_chips = set()
        down_chips.add((1, 1))
        vm = virtual_machine(2, 2, down_chips=down_chips)
        self.assertEqual(3, vm.n_chips)

        _chip = self._create_chip(2, 2)
        _chip._virtual = True
        vm.add_chip(_chip)
        self.assertEqual(vm.max_chip_x, 2)
        self.assertEqual(vm.max_chip_y, 2)
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
        self.assertTrue(4, count)

    def test_add_low_chip_with_down(self):
        down_chips = set()
        down_chips.add((1, 1))
        vm = virtual_machine(2, 2, down_chips=down_chips)
        self.assertEqual(3, vm.n_chips)
        self.assertFalse(vm.is_chip_at(1, 1))

        _chip = self._create_chip(1, 1)
        vm.add_chip(_chip)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEqual(4, vm.n_chips)

        self.assertTrue(vm.is_chip_at(1, 1))
        _good = vm.get_chip_at(1, 1)
        self.assertEqual(_chip, _good)

        _bad = vm.get_chip_at(2, 1)
        self.assertIsNone(_bad)

        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertTrue(4, count)

    def test_chips(self):
        vm = virtual_machine(2, 2)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(count, 4)

    def test_ethernet_chips_exist(self):
        vm = virtual_machine(width=48, height=24, with_wrap_arounds=True)
        for eth_chip in vm._ethernet_connected_chips:
            self.assertTrue(vm.get_chip_at(eth_chip.x, eth_chip.y),
                            "Eth chip location x={}, y={} not in "
                            "_configured_chips"
                            .format(eth_chip.x, eth_chip.y))

    def test_boot_chip(self):
        vm = virtual_machine(2, 2)
        self.assertNotEqual(vm.boot_chip, None)

    def test_get_chips_on_boards(self):
        vm = virtual_machine(width=24, height=36, with_wrap_arounds=True)
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
        assert(link.connected_chip_x == x)
        assert(link.connected_chip_y == y)
        assert(link.connected_link == link_id)

    def test_fpga_links_single_board(self):
        machine = virtual_machine(version=5)
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

        down_links = [(x, y, link) for _, _, _, x, y, link in fpga_links]

        machine = virtual_machine(
            width=12, height=12, with_wrap_arounds=True, down_links=down_links)
        machine.add_fpga_links()
        for ip, fpga, fpga_link, x, y, link in fpga_links:
            self._assert_fpga_link(machine, fpga, fpga_link, x, y, link, ip)

    def test_big(self):
        virtual_machine(
            width=240, height=240, with_wrap_arounds=True, validate=True)

    def test_size_2_2(self):
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
        hole = [(1, 1)]
        machine = virtual_machine(2, 2, down_chips=hole, validate=True)
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
        hole = [(1, 1), (7, 7), (8, 1), (8, 10), (1, 8), (9, 6)]
        machine = virtual_machine(12, 12, down_chips=hole, validate=True)
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
        hole = [(1, 1), (7, 7), (8, 13), (8, 10), (1, 8), (9, 6)]
        machine = virtual_machine(12, 16, down_chips=hole, validate=True)
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
        hole = [(1, 1), (7, 7), (8, 1), (8, 10), (13, 8), (9, 6)]
        machine = virtual_machine(16, 12, down_chips=hole, validate=True)
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
        hole = [(1, 1), (7, 7), (8, 13), (8, 10), (13, 8), (9, 6)]
        machine = virtual_machine(16, 16, down_chips=hole, validate=True)
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
        machine = virtual_machine(2, 2, validate=False)
        for x in range(-3, 3):
            for y in range(-3, 3):
                min1 = minimise_xyz((x, y, 0))
                min2 = machine._minimize_vector(x, y)
                self.assertEqual(min1, min2)

    def test_unreachable_incoming_chips(self):
        machine = virtual_machine(8, 8)

        # Delete links incoming to 3, 3
        down_links = [
            (2, 2, 1), (2, 3, 0), (3, 4, 5), (4, 4, 4), (4, 3, 3), (3, 2, 2)]
        for (x, y, link) in down_links:
            if machine.is_link_at(x, y, link):
                del machine._chips[x, y].router._links[link]

        new_machine = machine_repair(machine, True)
        self.assertFalse(new_machine.is_chip_at(3, 3))

    def test_unreachable_outgoing_chips(self):
        machine = virtual_machine(8, 8)

        # Delete links outgoing from 3, 3
        for link in range(6):
            if machine.is_link_at(3, 3, link):
                del machine._chips[3, 3].router._links[link]

        new_machine = machine_repair(machine, True)
        self.assertFalse(new_machine.is_chip_at(3, 3))

    def test_oneway_link_true(self):
        machine = virtual_machine(8, 8)

        # Delete links incoming to 3, 3
        down_links = [
            (3, 6, 0), (5, 4, 1), (3, 2, 5), (1, 3, 3)]
        for (x, y, link) in down_links:
            del machine._chips[x, y].router._links[link]
        new_machine = machine_repair(machine, True)
        self.assertIsNotNone(new_machine)

    def test_oneway_link_no_repair(self):
        machine = virtual_machine(8, 8)

        # Delete links incoming to 3, 3
        down_links = [
            (3, 6, 0), (5, 4, 1), (3, 2, 5), (1, 3, 3)]
        for (x, y, link) in down_links:
            if machine.is_link_at(x, y, link):
                del machine._chips[x, y].router._links[link]
        with self.assertRaises(SpinnMachineException):
            new_machine = machine_repair(machine, False)
            self.assertIsNotNone(new_machine)

    def test_removed_chip_repair(self):
        machine = virtual_machine(8, 8)

        del machine._chips[(3, 3)]
        new_machine = machine_repair(machine, False, [(3, 3)])
        self.assertIsNotNone(new_machine)
        self.assertFalse(new_machine.is_link_at(2, 2, 1))


if __name__ == '__main__':
    unittest.main()
