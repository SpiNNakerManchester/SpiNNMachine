import unittest
from spinn_utilities.ordered_set import OrderedSet
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
            self.assertTrue(p.processor_id in new_chip)
            self.assertEquals(new_chip[p.processor_id], p)
        self.assertEquals(new_chip.n_user_processors,
                          len(self._processors) - 1)
        with self.assertRaises(KeyError):
            self.assertIsNone(new_chip[42])
        self.assertEqual(
            new_chip.__repr__(),
            "[Chip: x=0, y=1, sdram=0 MB, ip_address=192.162.240.253, "
            "router=[Router: clock_speed=0 MHz, emergency_routing=False, "
            "available_entries=1024, links=["
            "[Link: source_x=0, source_y=0, source_link_id=0, "
            "destination_x=1, destination_y=1, default_from=2, default_to=2], "
            "[Link: source_x=0, source_y=1, source_link_id=1, "
            "destination_x=1, destination_y=0, default_from=5, default_to=5], "
            "[Link: source_x=1, source_y=1, source_link_id=2, "
            "destination_x=0, destination_y=0, default_from=0, default_to=0], "
            "[Link: source_x=1, source_y=0, source_link_id=3, "
            "destination_x=0, destination_y=1, default_from=3, default_to=3]"
            "]], processors=["
            "[CPU: id=0, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=1, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=2, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=3, clock_speed=0 MHz, monitor=True], "
            "[CPU: id=4, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=5, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=6, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=7, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=8, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=9, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=10, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=11, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=12, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=13, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=14, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=15, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=16, clock_speed=0 MHz, monitor=False], "
            "[CPU: id=17, clock_speed=0 MHz, monitor=False]], "
            "nearest_ethernet=0:0]")
        self.assertEqual(new_chip.tag_ids, OrderedSet([1, 2, 3, 4, 5, 6, 7]))
        self.assertFalse(new_chip.virtual)
        self.assertEqual(
            [p[0] for p in new_chip],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
        self.assertEqual(
            [p[1].is_monitor for p in new_chip],
            [False, False, False, True, False, False, False, False, False,
             False, False, False, False, False, False, False, False, False])
        self.assertTrue(new_chip.is_processor_with_id(3))

    def test_create_chip_with_duplicate_processors(self):
        flops = 1000

        processors = list()
        for i in range(18):
            processors.append(Processor(i, flops))
        processors.append(Processor(10, flops + 1))

        with self.assertRaises(SpinnMachineAlreadyExistsException):
            self._create_chip(self._x, self._y, processors, self._router,
                              self._sdram, self._ip)

    def test_get_first_none_monitor_processor(self):
        """ test the get_first_none_monitor_processor

        NOTE: Not sure if method being tested is required.
        """
        new_chip = self._create_chip(self._x, self._y, self._processors,
                                     self._router, self._sdram, self._ip)
        non_monitor = new_chip.get_first_none_monitor_processor()
        self.assertFalse(non_monitor.is_monitor)

    if __name__ == '__main__':
        unittest.main()
