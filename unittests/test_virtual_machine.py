import unittest
from spinn_machine import Processor, Link, SDRAM, Router, Chip, VirtualMachine
from spinn_machine.exceptions import (
    SpinnMachineAlreadyExistsException, SpinnMachineInvalidParameterException)


class TestVirtualMachine(unittest.TestCase):

    def _create_chip(self, x, y):
        # Create a list of processors.

        flops = 1000
        processors = list()
        for i in range(18):
            processors.append(Processor(i, flops, is_monitor=(i == 0)))

        (e, _, n, w, _, s) = range(6)
        links = list()
        links.append(Link(0, 0, 0, 1, 1, n, n))
        links.append(Link(0, 1, 1, 1, 0, s, s))
        links.append(Link(1, 1, 2, 0, 0, e, e))
        links.append(Link(1, 0, 3, 0, 1, w, w))
        _router = Router(links, False, 100, 1024)

        _sdram = SDRAM(128)
        nearest_ethernet_chip = (0, 0)
        _ip = "192.162.240.253"

        return Chip(x, y, processors, _router, _sdram,
                    nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], _ip)

    def test_illegal_vms(self):
        with self.assertRaises(SpinnMachineInvalidParameterException):
            VirtualMachine(width=-1, height=2)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            VirtualMachine(width=2, height=-1)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            VirtualMachine(version=0)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            VirtualMachine(version=3, with_wrap_arounds=True)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            VirtualMachine(version=3, width=12, height=12)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            VirtualMachine(version=5, with_wrap_arounds=True)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            VirtualMachine(version=5, width=12, height=12)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            VirtualMachine(with_wrap_arounds=True, width=15, height=15)

    def test_version_2(self):
        vm = VirtualMachine(version=2, with_wrap_arounds=None)
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
        self.assertEqual(str(vm),
                         "[VirtualMachine: max_x=1, max_y=1, n_chips=4]")
        self.assertEqual(vm.get_cores_and_link_count(), (72, 8))
        count = 0
        for _chip in vm.get_chips_on_board(vm.get_chip_at(1, 1)):
            count += 1
        self.assertEqual(4, count)

    def test_2_with_wrapparound(self):
        vm = VirtualMachine(height=2, width=2, with_wrap_arounds=True)
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
        vm = VirtualMachine(height=2, width=2, with_wrap_arounds=False)
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
        vm = VirtualMachine(version=5)
        self.assertEqual(vm.max_chip_x, 7)
        self.assertEqual(vm.max_chip_y, 7)
        self.assertEqual(48, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertTrue(vm.is_chip_at(4, 4))
        self.assertFalse(vm.is_chip_at(0, 4))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(240, count)

    def test_8_by_8(self):
        vm = VirtualMachine(
            width=8, height=8, version=None, with_wrap_arounds=False)
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
        vm = VirtualMachine(height=12, width=12, version=None,
                            with_wrap_arounds=None)
        self.assertEqual(vm.max_chip_x, 11)
        self.assertEqual(vm.max_chip_y, 11)
        self.assertEqual(144, vm.n_chips)
        self.assertEqual(3, len(vm.ethernet_connected_chips))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(864, count)
        count = 0
        for _chip in vm.get_chips_on_board(vm.get_chip_at(1, 1)):
            count += 1
        self.assertEqual(48, count)

    def test_version_5_guess_8x8(self):
        vm = VirtualMachine(height=8, width=8, version=None,
                            with_wrap_arounds=None)
        self.assertEqual(vm.max_chip_x, 7)
        self.assertEqual(vm.max_chip_y, 7)
        self.assertEqual(48, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(240, count)

    def test_version_5_hole(self):
        hole = [(3, 3)]
        vm = VirtualMachine(version=5, down_chips=hole)
        self.assertEqual(vm.max_chip_x, 7)
        self.assertEqual(vm.max_chip_y, 7)
        self.assertEqual(47, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertFalse(vm.is_link_at(3, 3, 2))
        self.assertFalse(vm.is_link_at(3, 2, 2))
        count = sum(1 for _chip in vm.chips for _link in _chip.router.links)
        self.assertEqual(228, count)

    def test_new_vm_no_monitor(self):
        n_cpus = 11
        vm = VirtualMachine(2, 2, n_cpus_per_chip=n_cpus, with_monitors=False)
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
        vm = VirtualMachine(2, 2, n_cpus_per_chip=n_cpus, with_monitors=True)
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
        vm = VirtualMachine(2, 2)
        self.assertEqual(4, vm.n_chips)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertTrue(4, count)

    def test_down_chip(self):
        down_chips = set()
        down_chips.add((1, 1))
        vm = VirtualMachine(2, 2, down_chips=down_chips)
        self.assertEqual(3, vm.n_chips)
        count = 0
        for _chip in vm.chip_coordinates:
            count += 1
            self.assertNotIn(_chip, down_chips)
        self.assertTrue(3, count)

    def test_add_existing_chip(self):
        vm = VirtualMachine(2, 2)
        _chip = self._create_chip(1, 1)
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            vm.add_chip(_chip)

    def test_weird_size(self):
        with self.assertRaises(SpinnMachineInvalidParameterException):
            VirtualMachine(5, 7)

    def test_12_n_plus4_12_m_4(self):
        size_x = 12 * 5
        size_y = 12 * 7
        vm = VirtualMachine(size_x + 4, size_y + 4)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_12_n_12_m(self):
        size_x = 12 * 5
        size_y = 12 * 7
        vm = VirtualMachine(size_x, size_y, with_wrap_arounds=True)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_add__chip(self):
        vm = VirtualMachine(2, 2)

        _chip = self._create_chip(2, 2)
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
        vm = VirtualMachine(2, 2, down_chips=down_chips)
        self.assertEqual(3, vm.n_chips)

        _chip = self._create_chip(2, 2)
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
        vm = VirtualMachine(2, 2, down_chips=down_chips)
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
        vm = VirtualMachine(2, 2)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(count, 4)

    def test_ethernet_chips_exist(self):
        vm = VirtualMachine(width=48, height=24, with_wrap_arounds=True)
        for eth_chip in vm._ethernet_connected_chips:
            self.assertTrue(vm.get_chip_at(eth_chip.x, eth_chip.y),
                            "Eth chip location x={}, y={} not in "
                            "_configured_chips"
                            .format(eth_chip.x, eth_chip.y))

    def test_boot_chip(self):
        vm = VirtualMachine(2, 2)
        self.assertNotEqual(vm.boot_chip, None)

    def test_get_chips_on_boards(self):
        vm = VirtualMachine(width=24, height=36, with_wrap_arounds=True)
        # check each chip appears only once on the entire board
        count00 = 0
        count50 = 0
        count04 = 0
        count2436 = 0
        for eth_chip in vm._ethernet_connected_chips:
            list_of_chips = list(vm.get_chips_on_board(eth_chip))
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

    def test_big(self):
        VirtualMachine(width=240, height=240, with_wrap_arounds=True)


if __name__ == '__main__':
    unittest.main()
