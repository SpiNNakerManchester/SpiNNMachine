"""
test for testing the python representation of a spinnaker machine
"""

# spinnmachine imports
from spinn_machine import processor as proc, link as link, sdram as sdram, \
    router as router, chip as chip
import spinn_machine.exceptions as exc
import spinn_machine.machine as machine

# general imports
import unittest


class SpinnMachineTestCase(unittest.TestCase):
    """
    test for testing the python representation of a spinnaker machine
    """

    def setUp(self):
        self._sdram = sdram.SDRAM(128)

        (e, _, n, w, _, s) = range(6)
        links = list()
        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        self._router = router.Router(links, False, 100, 1024)

        self._nearest_ethernet_chip = (0, 0)

        self._ip = "192.162.240.253"

    def _create_processors(self, monitor=3, number=18):
        """
        Create a list of processors.

        As some test change the processors this must be called each time.

        :param monitor: Id of process to make the monitor
        :type monitor: int
        """
        flops = 1000
        processors = list()
        for i in range(number):
            if i == monitor:
                processors.append(proc.Processor(i, flops, is_monitor=True))
            else:
                processors.append(proc.Processor(i, flops))
        return processors

    def _create_chip(self, x, y, processors):
        return chip.Chip(x, y, processors, self._router, self._sdram,
                         self._nearest_ethernet_chip[0],
                         self._nearest_ethernet_chip[1], self._ip)

    def _create_chips(self, processors=None, monitor=3):
        if not processors:
            processors = self._create_processors(monitor)
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(self._create_chip(x, y, processors))
        return chips

    def test_create_new_machine(self):
        """
        test creating a new machine
        """
        processors = self._create_processors()

        chips = self._create_chips(processors)

        new_machine = machine.Machine(chips, 0, 0)

        self.assertEqual(new_machine.max_chip_x, 4)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            self.assertEqual(c.ip_address, self._ip)
            self.assertEqual(c.sdram, self._sdram)
            self.assertEqual(c.router, self._router)
            for p in processors:
                self.assertTrue(p in c.processors)

    def test_create_new_machine_with_invalid_chips(self):
        """
        check that building a machine with invalid chips causes errors

        :rtype: None
        """
        chips = self._create_chips()
        chips.append(chip.Chip(
            0, 0, self._create_processors(), self._router, self._sdram,
            self._nearest_ethernet_chip[0],
            self._nearest_ethernet_chip[1], self._ip))
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            machine.Machine(chips, 0, 0)

    def test_machine_add_chip(self):
        """
        test the add_chip method of the machine object

        :rtype: None
        """
        processors = self._create_processors()
        new_machine = machine.Machine(self._create_chips(processors), 0, 0)
        processor = list()
        processor.append(proc.Processor(100, 100, False))
        extra_chip = self._create_chip(5, 0, processor)
        new_machine.add_chip(extra_chip)
        self.assertEqual(new_machine.max_chip_x, 5)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            self.assertEqual(c.ip_address, self._ip)
            self.assertEqual(c.sdram, self._sdram)
            self.assertEqual(c.router, self._router)
            if c is extra_chip:
                with self.assertRaises(AssertionError):
                    for p in c.processors:
                        self.assertTrue(p in processors)

    def test_machine_add_duplicate_chip(self):
        """
        test if adding the same chip twice causes an error

        :rtype: None
        """
        chips = self._create_chips()
        new_machine = machine.Machine(chips, 0, 0)
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            new_machine.add_chip(chips[3])

    def test_machine_add_chips(self):
        """
        check that adding range of chips works

        :rtype: None
        """
        processors = self._create_processors()
        chips = self._create_chips(processors)
        new_machine = machine.Machine(chips, 0, 0)

        extra_chips = list()
        extra_chips.append(self._create_chip(5, 0, processors))
        extra_chips.append(self._create_chip(5, 1, processors))
        extra_chips.append(self._create_chip(5, 2, processors))
        extra_chips.append(self._create_chip(5, 3, processors))

        new_machine.add_chips(extra_chips)
        self.assertEqual(new_machine.max_chip_x, 5)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            self.assertEqual(c.ip_address, self._ip)
            self.assertEqual(c.sdram, self._sdram)
            self.assertEqual(c.router, self._router)
            for p in processors:
                self.assertTrue(p in c.processors)

    def test_machine_add_duplicate_chips(self):
        """
        test the add_chips method of the machine with duplicate chips.
        should produce an error

        :rtype: None
        """
        chips = self._create_chips()
        new_machine = machine.Machine(chips, 0, 0)

        processors = self._create_processors()
        extra_chips = list()
        extra_chips.append(self._create_chip(6, 0, processors))
        extra_chips.append(chips[3])

        self.assertRaises(exc.SpinnMachineAlreadyExistsException,
                          new_machine.add_chips, extra_chips)

    def test_machine_get_chip_at(self):
        """
        test the get_chip_at function from the machine with a valid request

        :rtype: None
        """
        chips = self._create_chips()
        new_machine = machine.Machine(chips, 0, 0)
        self.assertEqual(chips[0], new_machine.get_chip_at(0, 0))

    def test_machine_get_chip_at_invalid_location(self):
        """
        test the machines get_chip_at function with a location thats invalid,
        should return None and not produce an error

        :rtype: None
        """
        chips = self._create_chips()

        new_machine = machine.Machine(chips, 0, 0)
        self.assertEqual(None, new_machine.get_chip_at(10, 0))

    def test_machine_is_chip_at_true(self):
        """
        test the is_chip_at function of the machine with a position to
        request which does indeed contain a chip

        :rtype: None
        """
        chips = self._create_chips()

        new_machine = machine.Machine(chips, 0, 0)
        self.assertTrue(new_machine.is_chip_at(3, 0))

    def test_machine_is_chip_at_false(self):
        """
        test the is_chip_at function of the machine with a position to
        request which does not contain a chip

        :rtype: None
        """
        chips = self._create_chips()
        new_machine = machine.Machine(chips, 0, 0)
        self.assertFalse(new_machine.is_chip_at(10, 0))

    def test_reserve_system_processors(self):
        processors = self._create_processors()
        chips = self._create_chips(processors)
        new_machine = machine.Machine(chips, 0, 0)
        self.assertEquals(new_machine.maximum_user_cores_on_chip,
                          len(processors) - 1)

        new_machine.reserve_system_processors()
        self.assertEquals(new_machine.maximum_user_cores_on_chip,
                          len(processors) - 2)

    def test_reserve_system_processors_different(self):
        chips = list()
        for x in range(2):
            for y in range(2):
                processors = self._create_processors(
                    monitor=1 + x + y, number=5 + x + y)
                chips.append(self._create_chip(x, y, processors))
        # processors coming out will be biggest list

        new_machine = machine.Machine(chips, 0, 0)
        self.assertEquals(new_machine.maximum_user_cores_on_chip,
                          len(processors) - 1)

        new_machine.reserve_system_processors()
        self.assertEquals(new_machine.maximum_user_cores_on_chip,
                          len(processors) - 2)


if __name__ == '__main__':
    unittest.main()
