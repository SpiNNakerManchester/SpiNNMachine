import unittest
from spinn_machine import processor as proc, link as link, sdram as sdram, \
    router as router, chip as chip
import spinn_machine.exceptions as exc
import spinn_machine.machine as machine


class MyTestCase(unittest.TestCase):
    def test_create_new_machine(self):
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
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(x, y, processors, r, _sdram, ip))

        new_machine = machine.Machine(chips)

        self.assertEqual(new_machine.max_chip_x, 4)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            self.assertEqual(c.ip_address, ip)
            self.assertEqual(c.sdram, _sdram)
            self.assertEqual(c.router, r)
            for p in processors:
                self.assertTrue(p in c.processors)

    def test_create_new_machine_with_invalid_chips(self):
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
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
            chips = list()
            for x in range(5):
                for y in range(5):
                    chips.append(chip.Chip(x, y, processors, r, _sdram, ip))
            chips.append(chip.Chip(0, 0, processors, r, _sdram, ip))
            machine.Machine(chips)

    def test_machine_add_chip(self):
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
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(x, y, processors, r, _sdram, ip))

        new_machine = machine.Machine(chips)
        processor = list()
        processor.append(proc.Processor(100, 100, False))
        extra_chip = chip.Chip(5, 0, processor, r, _sdram, ip)
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
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
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
            chips = list()
            for x in range(5):
                for y in range(5):
                    chips.append(chip.Chip(x, y, processors, r, _sdram, ip))

            new_machine = machine.Machine(chips)
            new_machine.add_chip(chips[3])

    def test_machine_add_chips(self):
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

        extra_chips = list()
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(x, y, processors, r, _sdram, ip))
                if x == 0:
                    extra_chips.append(
                        chip.Chip(x + 5, y, processors, r, _sdram, ip))

        new_machine = machine.Machine(chips)
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
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
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
            chips = list()
            extra_chips = list()
            for x in range(5):
                for y in range(5):
                    chips.append(chip.Chip(x, y, processors, r, _sdram, ip))
                    if x == 0:
                        extra_chips.append(
                            chip.Chip(x, y, processors, r, _sdram, ip))

            new_machine = machine.Machine(chips)
            new_machine.add_chip(chips[3])

    def test_machine_get_chip_at(self):
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
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(x, y, processors, r, _sdram, ip))

        new_machine = machine.Machine(chips)
        self.assertEqual(chips[0], new_machine.get_chip_at(0, 0))

    def test_machine_get_chip_at_invalid_location(self):
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
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(x, y, processors, r, _sdram, ip))

        new_machine = machine.Machine(chips)
        self.assertEqual(None, new_machine.get_chip_at(10, 0))

    def test_machine_is_chip_at_true(self):
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
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(x, y, processors, r, _sdram, ip))

        new_machine = machine.Machine(chips)
        self.assertTrue(new_machine.is_chip_at(3, 0))

    def test_machine_is_chip_at_false(self):
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
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(x, y, processors, r, _sdram, ip))

        new_machine = machine.Machine(chips)
        self.assertFalse(new_machine.is_chip_at(10, 0))


if __name__ == '__main__':
    unittest.main()
