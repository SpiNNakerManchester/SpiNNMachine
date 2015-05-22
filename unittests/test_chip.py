import unittest
from spinn_machine import processor as proc, link as link, sdram as sdram, \
    router as router, chip as chip
import spinn_machine.exceptions as exc


class TestingChip(unittest.TestCase):
    def test_create_chip(self):
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)
        x = 0
        y = 1

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        ip = "192.162.240.253"
        nearest_ethernet_chip = (0, 0)

        new_chip = chip.Chip(
            x, y, processors, r, _sdram, nearest_ethernet_chip[0],
            nearest_ethernet_chip[1], ip)

        self.assertEqual(new_chip.x, x)
        self.assertEqual(new_chip.y, y)
        self.assertEqual(new_chip.ip_address, ip)
        self.assertEqual(new_chip.sdram, _sdram)
        self.assertEqual(new_chip.router, r)
        for p in processors:
            self.assertTrue(p in new_chip.processors)

    def test_create_chip_with_duplicate_processors(self):
        flops = 1000
        (e, ne, n, w, sw, s) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))
        processors.append(proc.Processor(10, flops + 1))

        links = list()
        links.append(link.Link(0, 0, 0, 0, 1, s, s))

        _sdram = sdram.SDRAM(128)
        x = 0
        y = 1

        links = list()

        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)
        nearest_ethernet_chip = (0, 0)
        ip = "192.162.240.253"

        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            chip.Chip(x, y, processors, r, _sdram, nearest_ethernet_chip[0],
                      nearest_ethernet_chip[1], ip)


if __name__ == '__main__':
    unittest.main()
