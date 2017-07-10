import unittest
from spinn_machine import Processor, Link, SDRAM, Router, Chip
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException


class TestingChip(unittest.TestCase):

    def setUp(self):
        self._x = 0
        self._y = 1

        # create processor
        self._monitor_id = 3
        flops = 1000
        self._processors = list()
        for i in range(18):
            if i == self._monitor_id:
                self._processors.append(Processor(i, flops, is_monitor=True))
            else:
                self._processors.append(Processor(i, flops))

        # create router
        (e, _, n, w, _, s) = range(6)
        links = list()
        links.append(Link(0, 0, 0, 1, 1, n, n))
        links.append(Link(0, 1, 1, 1, 0, s, s))
        links.append(Link(1, 1, 2, 0, 0, e, e))
        links.append(Link(1, 0, 3, 0, 1, w, w))
        self._router = Router(links, False, 100, 1024)

        self._sdram = SDRAM(128)
        self._ip = "192.162.240.253"

    def _create_chip(self, x, y, processors, r, sdram, ip):
        nearest_ethernet_chip = (0, 0)

        return Chip(x, y, processors, r, sdram, nearest_ethernet_chip[0],
                    nearest_ethernet_chip[1], ip)

    def test_create_chip(self):
        new_chip = self._create_chip(self._x, self._y, self._processors,
                                     self._router, self._sdram, self._ip)

        self.assertEqual(new_chip.x, self._x)
        self.assertEqual(new_chip.y, self._y)
        self.assertEqual(new_chip.ip_address, self._ip)
        self.assertEqual(new_chip.sdram, self._sdram)
        self.assertEqual(new_chip.router, self._router)
        for p in self._processors:
            # warning the chip will clone a processor if it changes it
            # For example if reserve_a_system_processor() is called
            self.assertTrue(p in new_chip.processors)
        self.assertEquals(new_chip.n_user_processors,
                          len(self._processors) - 1)

    def test_create_chip_with_duplicate_processors(self):
        flops = 1000

        processors = list()
        for i in range(18):
            processors.append(Processor(i, flops))
        processors.append(Processor(10, flops + 1))

        with self.assertRaises(SpinnMachineAlreadyExistsException):
            self._create_chip(self._x, self._y, processors, self._router,
                              self._sdram, self._ip)

    def test_reserve_a_system_processor(self):
        new_chip = self._create_chip(self._x, self._y, self._processors,
                                     self._router, self._sdram, self._ip)
        self.assertEquals(new_chip.n_user_processors,
                          len(self._processors) - 1)

        monitor = new_chip.get_processor_with_id(self._monitor_id)
        self.assertTrue(monitor.is_monitor)

        for processor in new_chip.processors:
            self.assertFalse(processor.is_monitor and
                             processor.processor_id != self._monitor_id)

        new_chip.reserve_a_system_processor()
        self.assertEquals(new_chip.n_user_processors,
                          len(self._processors) - 2)

        count = 0
        for processor in new_chip.processors:
            if (processor.is_monitor and
                    (processor.processor_id != self._monitor_id)):
                count += 1
        self.assertEquals(count, 1)

    def test_get_first_none_monitor_processor(self):
        """
        test the get_first_none_monitor_processor

        NOTE: Not sure if method being tested is required.
        """
        new_chip = self._create_chip(self._x, self._y, self._processors,
                                     self._router, self._sdram, self._ip)
        non_monitor = new_chip.get_first_none_monitor_processor()
        self.assertFalse(non_monitor.is_monitor)

    if __name__ == '__main__':
        unittest.main()
