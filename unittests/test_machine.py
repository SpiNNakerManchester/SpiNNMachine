"""
test for testing the python represnetaiton of a spinnaker machine
"""

# spinnmanchine imports
from spinn_machine import processor as proc, link as link, sdram as sdram, \
    router as router, chip as chip
import spinn_machine.exceptions as exc
import spinn_machine.machine as machine

# general imports
import unittest


class SpinnMachineTestCase(unittest.TestCase):
    """
    test for testing the python represnetaiton of a spinnaker machine
    """

    def test_create_new_machine(self):
        """
        test creating a new machine

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        nearest_ethernet_chip = (0, 0)
        ip = "192.162.240.253"
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(
                    chip.Chip(
                        x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                        nearest_ethernet_chip[1], ip))

        new_machine = machine.Machine(chips, 0, 0)

        self.assertEqual(new_machine.max_chip_x, 4)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            self.assertEqual(c.ip_address, ip)
            self.assertEqual(c.sdram, _sdram)
            self.assertEqual(c.router, r)
            for p in processors:
                self.assertTrue(p in c.processors)

    def test_create_new_machine_with_invalid_chips(self):
        """
        check that building a machine with invalid chips causes errors

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))
        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        nearest_ethernet_chip = (0, 0)
        ip = "192.162.240.253"

        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(
                    x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip))
        chips.append(chip.Chip(
            0, 0, processors, r, _sdram, nearest_ethernet_chip[0],
            nearest_ethernet_chip[1], ip))
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            machine.Machine(chips, 0, 0)

    def test_machine_add_chip(self):
        """
        test the add_chip emthod of the machine object

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        nearest_ethernet_chip = (0, 0)
        ip = "192.162.240.253"
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(
                    x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip))

        new_machine = machine.Machine(chips, 0, 0)
        processor = list()
        processor.append(proc.Processor(100, 100, False))
        extra_chip = chip.Chip(
            5, 0, processor, r, _sdram, nearest_ethernet_chip[0],
            nearest_ethernet_chip[1], ip)
        new_machine.add_chip(extra_chip)
        self.assertEqual(new_machine.max_chip_x, 5)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            self.assertEqual(c.ip_address, ip)
            self.assertEqual(c.sdram, _sdram)
            self.assertEqual(c.router, r)
            if c is extra_chip:
                with self.assertRaises(AssertionError):
                    for p in c.processors:
                        self.assertTrue(p in processors)

    def test_machine_add_duplicate_chip(self):
        """
        test if adding the same chip twice causes an error

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        nearest_ethernet_chip = (0, 0)
        ip = "192.162.240.253"
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(
                    x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip))

        new_machine = machine.Machine(chips, 0, 0)
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            new_machine.add_chip(chips[3])

    def test_machine_add_chips(self):
        """
        check that adding range of chips works

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        ip = "192.162.240.253"
        nearest_ethernet_chip = (0, 0)

        extra_chips = list()
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(
                    x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip))
                if x == 0:
                    extra_chips.append(
                        chip.Chip(
                            x + 5, y, processors, r, _sdram,
                            nearest_ethernet_chip[0], nearest_ethernet_chip[1],
                            ip))

        new_machine = machine.Machine(chips, 0, 0)
        new_machine.add_chips(extra_chips)

        self.assertEqual(new_machine.max_chip_x, 5)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            self.assertEqual(c.ip_address, ip)
            self.assertEqual(c.sdram, _sdram)
            self.assertEqual(c.router, r)
            for p in processors:
                self.assertTrue(p in c.processors)

    def test_machine_add_duplicate_chips(self):
        """
        test the add_chips emthof of the machine with duplicate chips.
        should produce an error

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        ip = "192.162.240.253"
        nearest_ethernet_chip = (0, 0)
        chips = list()
        extra_chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(
                    x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip))
                if x == 0:
                    extra_chips.append(
                        chip.Chip(
                            x, y, processors, r, _sdram,
                            nearest_ethernet_chip[0], nearest_ethernet_chip[1],
                            ip))

        new_machine = machine.Machine(chips, 0, 0)
        self.assertRaises(exc.SpinnMachineAlreadyExistsException,
                          new_machine.add_chips, extra_chips)

    def test_machine_get_chip_at(self):
        """
        test the get_chip_at function from the machine with a valid request

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        ip = "192.162.240.253"
        nearest_ethernet_chip = (0, 0)
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(
                    x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip))

        new_machine = machine.Machine(chips, 0, 0)
        self.assertEqual(chips[0], new_machine.get_chip_at(0, 0))

    def test_machine_get_chip_at_invalid_location(self):
        """
        test the machines get_chip_at function with a location thats invalid,
        should return None and not produce an error

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        ip = "192.162.240.253"
        nearest_ethernet_chip = (0, 0)
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(
                    x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip))

        new_machine = machine.Machine(chips, 0, 0)
        self.assertEqual(None, new_machine.get_chip_at(10, 0))

    def test_machine_is_chip_at_true(self):
        """
        test the is_chip_at function of the machine with a postiion to
        request whcih does indeed contain a chip

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        ip = "192.162.240.253"
        nearest_ethernet_chip = (0, 0)
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(
                    x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip))

        new_machine = machine.Machine(chips, 0, 0)
        self.assertTrue(new_machine.is_chip_at(3, 0))

    def test_machine_is_chip_at_false(self):
        """
        test the is_chip_at function of the machine with a postiion to
        request whcih does not contain a chip

        :rtype: None
        """
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        ip = "192.162.240.253"
        nearest_ethernet_chip = (0, 0)
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(
                    x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip))

        new_machine = machine.Machine(chips, 0, 0)
        self.assertFalse(new_machine.is_chip_at(10, 0))


if __name__ == '__main__':
    unittest.main()
