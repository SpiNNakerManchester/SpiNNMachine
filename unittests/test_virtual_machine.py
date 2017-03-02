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

        (e, ne, n, w, sw, s) = range(6)
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

    def test_new_vm_no_monitor(self):
        n_cpus = 18
        vm = virtual_machine.VirtualMachine(2, 2, n_cpus_per_chip=n_cpus,
                                            with_monitors=False)
        _chip = vm.get_chip_at(1, 1)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEquals(n_cpus, vm.maximum_user_cores_on_chip)

    def test_new_vm_with_monitor(self):
        n_cpus = 18
        vm = virtual_machine.VirtualMachine(2, 2, n_cpus_per_chip=n_cpus,
                                            with_monitors=True)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEquals(n_cpus-1, vm.maximum_user_cores_on_chip)

    def test_iter_chips(self):
        vm = virtual_machine.VirtualMachine(2, 2)
        self.assertEquals(4, vm.n_chips)
        count = 0
        for chip in vm.chips:
            count += 1
        self.assertTrue(4, count)

    def test_down_chip(self):
        down_chips = set()
        down_chips.add((1,1))
        vm = virtual_machine.VirtualMachine(2, 2, down_chips=down_chips)
        self.assertEquals(3, vm.n_chips)
        count = 0
        for chip in vm.chip_coordinates:
            count += 1
            self.assertNotIn(chip, down_chips)
        self.assertTrue(3, count)


    def test_add_existing_chip(self):
        vm = virtual_machine.VirtualMachine(2, 2)
        _chip = self._create_chip(1, 1)
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            vm.add_chip(_chip)

    def test_add__chip(self):
        vm = virtual_machine.VirtualMachine(2, 2)

        _chip = self._create_chip(2, 2)
        vm.add_chip(_chip)
        self.assertEqual(vm.max_chip_x, 2)
        self.assertEqual(vm.max_chip_y, 2)
        self.assertEquals(5, vm.n_chips)

        self.assertTrue(vm.is_chip_at(2, 2))
        _good = vm.get_chip_at(2, 2)
        self.assertEqual(_chip, _good)

        _bad = vm.get_chip_at(2, 1)
        self.assertIsNone(_bad)

        count = 0
        for chip in vm.chips:
            count += 1
        self.assertTrue(5, count)

    def test_add_high_chip_with_down(self):
        down_chips = set()
        down_chips.add((1,1))
        vm = virtual_machine.VirtualMachine(2, 2, down_chips=down_chips)
        self.assertEquals(3, vm.n_chips)

        _chip = self._create_chip(2, 2)
        vm.add_chip(_chip)
        self.assertEqual(vm.max_chip_x, 2)
        self.assertEqual(vm.max_chip_y, 2)
        self.assertEquals(4, vm.n_chips)

        self.assertTrue(vm.is_chip_at(2, 2))
        _good = vm.get_chip_at(2, 2)
        self.assertEqual(_chip, _good)

        _bad = vm.get_chip_at(2, 1)
        self.assertIsNone(_bad)

        _down = vm.get_chip_at(1, 1)
        self.assertIsNone(_down)

        count = 0
        for chip in vm.chips:
            count += 1
        self.assertTrue(4, count)

    def test_add_low_chip_with_down(self):
        down_chips = set()
        down_chips.add((1,1))
        vm = virtual_machine.VirtualMachine(2, 2, down_chips=down_chips)
        self.assertEquals(3, vm.n_chips)
        self.assertFalse(vm.is_chip_at(1, 1))

        _chip = self._create_chip(1, 1)
        vm.add_chip(_chip)
        self.assertEqual(vm.max_chip_x, 1)
        self.assertEqual(vm.max_chip_y, 1)
        self.assertEquals(4, vm.n_chips)

        self.assertTrue(vm.is_chip_at(1, 1))
        _good = vm.get_chip_at(1, 1)
        self.assertEqual(_chip, _good)

        _bad = vm.get_chip_at(2, 1)
        self.assertIsNone(_bad)

        count = 0
        for chip in vm.chips:
            count += 1
        self.assertTrue(4, count)

    def test_chips(self):
        vm = virtual_machine.VirtualMachine(2,2)
        count = 0
        for chip in vm.chips:
            count += 1
        self.assertEquals(count, 4)

    def test_reserve_system_processors_different(self):
        n_chips = 18
        vm = virtual_machine.VirtualMachine(2, 2, n_cpus_per_chip=n_chips,
                                            with_monitors=True)
        self.assertEquals(vm.maximum_user_cores_on_chip,
                          n_chips - 1)

        vm.reserve_system_processors()
        self.assertEquals(vm.maximum_user_cores_on_chip,
                          n_chips-2)

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

