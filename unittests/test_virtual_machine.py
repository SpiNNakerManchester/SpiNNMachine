import unittest
from spinn_machine import processor as proc, link as link, sdram as sdram,\
    router as router, chip as chip, virtual_machine as virtual_machine
import spinn_machine.exceptions as exc


class TestVirtualMachine(unittest.TestCase):

    def _create_chip(self, x, y):
        # Create a list of processors.

        flops = 1000
        processors = list()
        for i in range(18):
            if i == 0:
                processors.append(proc.Processor(i, flops, is_monitor=True))
            else:
                processors.append(proc.Processor(i, flops))

        (e, _, n, w, _, s) = range(6)
        links = list()
        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        _router = router.Router(links, False, 100, 1024)

        _sdram = sdram.SDRAM(128)
        nearest_ethernet_chip = (0, 0)
        _ip = "192.162.240.253"

        return chip.Chip(x, y, processors, _router, _sdram,
                         nearest_ethernet_chip[0],
                         nearest_ethernet_chip[1], _ip)

    def test_version_2(self):
        vm = virtual_machine.VirtualMachine(version=2, with_wrap_arounds=None)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEqual(4, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertTrue(vm.is_link_at(0, 0, 5))
        self.assertTrue(vm.is_link_at(0, 1, 2))
        self.assertFalse(vm.is_link_at(0, 0, 4))
        self.assertFalse(vm.is_link_at(0, 1, 3))
        count = 0
        for _chip in vm.chips:
            for _link in _chip.router.links:
                count += 1
        self.assertEqual(16, count)

    def test_2_with_wrapparound(self):
        vm = virtual_machine.VirtualMachine(height=2, width=2,
                                            with_wrap_arounds=True)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEqual(4, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertTrue(vm.is_link_at(0, 0, 5))
        self.assertTrue(vm.is_link_at(0, 1, 2))
        self.assertTrue(vm.is_link_at(0, 0, 4))
        self.assertTrue(vm.is_link_at(0, 1, 3))
        count = 0
        for _chip in vm.chips:
            for _link in _chip.router.links:
                count += 1
        self.assertEqual(24, count)

    def test_2_no_wrapparound(self):
        vm = virtual_machine.VirtualMachine(height=2, width=2,
                                            with_wrap_arounds=False)
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
        vm = virtual_machine.VirtualMachine(version=5)
        self.assertEqual(vm.max_chip_x, 7)
        self.assertEqual(vm.max_chip_y, 7)
        self.assertEqual(48, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        count = 0
        for _chip in vm.chips:
            for _link in _chip.router.links:
                count += 1
        self.assertEqual(240, count)

    def test_version_5_hole(self):
        hole = [(3, 3)]
        vm = virtual_machine.VirtualMachine(version=5, down_chips=hole)
        self.assertEqual(vm.max_chip_x, 7)
        self.assertEqual(vm.max_chip_y, 7)
        self.assertEqual(47, vm.n_chips)
        self.assertEqual(1, len(vm.ethernet_connected_chips))
        self.assertFalse(vm.is_link_at(3, 3, 2))
        self.assertFalse(vm.is_link_at(3, 2, 2))
        count = 0
        for _chip in vm.chips:
            for _link in _chip.router.links:
                count += 1
        self.assertEqual(228, count)

    def test_new_vm_no_monitor(self):
        n_cpus = 11
        vm = virtual_machine.VirtualMachine(2, 2, n_cpus_per_chip=n_cpus,
                                            with_monitors=False)
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
        vm = virtual_machine.VirtualMachine(2, 2, n_cpus_per_chip=n_cpus,
                                            with_monitors=True)
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
        vm = virtual_machine.VirtualMachine(2, 2)
        self.assertEqual(4, vm.n_chips)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertTrue(4, count)

    def test_down_chip(self):
        down_chips = set()
        down_chips.add((1, 1))
        vm = virtual_machine.VirtualMachine(2, 2, down_chips=down_chips)
        self.assertEqual(3, vm.n_chips)
        count = 0
        for _chip in vm.chip_coordinates:
            count += 1
            self.assertNotIn(chip, down_chips)
        self.assertTrue(3, count)

    def test_add_existing_chip(self):
        vm = virtual_machine.VirtualMachine(2, 2)
        _chip = self._create_chip(1, 1)
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            vm.add_chip(_chip)

    def test_weird_size(self):
        with self.assertRaises(exc.SpinnMachineInvalidParameterException):
            virtual_machine.VirtualMachine(5, 7)

    def test_12_n_plus4_12_m_4(self):
        size_x = 12 * 5
        size_y = 12 * 7
        vm = virtual_machine.VirtualMachine(size_x + 4, size_y + 4)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_12_n_12_m(self):
        size_x = 12 * 5
        size_y = 12 * 7
        vm = virtual_machine.VirtualMachine(size_x, size_y,
                                            with_wrap_arounds=True)
        self.assertEqual(size_x * size_y, vm.n_chips)

    def test_add__chip(self):
        vm = virtual_machine.VirtualMachine(2, 2)

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
        vm = virtual_machine.VirtualMachine(2, 2, down_chips=down_chips)
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
        vm = virtual_machine.VirtualMachine(2, 2, down_chips=down_chips)
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
        vm = virtual_machine.VirtualMachine(2, 2)
        count = 0
        for _chip in vm.chips:
            count += 1
        self.assertEqual(count, 4)

    def test_reserve_system_processors_different(self):
        n_chips = 18
        vm = virtual_machine.VirtualMachine(2, 2, n_cpus_per_chip=n_chips,
                                            with_monitors=True)
        self.assertEqual(vm.maximum_user_cores_on_chip,
                         n_chips - 1)

        vm.reserve_system_processors()
        self.assertEqual(vm.maximum_user_cores_on_chip,
                         n_chips - 2)

    def test_ethernet_chips_exist(self):
        vm = virtual_machine.VirtualMachine(width=48, height=24,
                                            with_wrap_arounds=True)
        for eth_chip in vm._ethernet_connected_chips:
            self.assertTrue(vm.get_chip_at(eth_chip.x, eth_chip.y),
                            "Eth chip location x={}, y={} not in "
                            "_configured_chips"
                            .format(eth_chip.x, eth_chip.y))

    @unittest.skip("skipping test_initlize_neighbour_links_for_other_boards")
    def test_initlize_neighbour_links_for_other_boards(self):
        self.assertEqual(True, False, "Test not implemented yet")

    @unittest.skip("skipping test_initlize_neighbour_links_for_4_chip_board")
    def test_initlize_neighbour_links_for_4_chip_board(self):
        self.assertEqual(True, False, "Test not implemented yet")

    @unittest.skip("skipping test_calculate_links")
    def test_calculate_links(self):
        self.assertEqual(True, False, "Test not implemented yet")


if __name__ == '__main__':
    unittest.main()
