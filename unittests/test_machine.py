# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
test for testing the python representation of a spinnaker machine
"""
import unittest
from spinn_machine import (
    Processor, Link, SDRAM, Router, Chip, machine_from_chips,
    machine_from_size)
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException


class SpinnMachineTestCase(unittest.TestCase):
    """
    test for testing the python representation of a spinnaker machine
    """

    def setUp(self):
        self._sdram = SDRAM(128)

        links = list()
        links.append(Link(0, 0, 0, 1, 1))
        links.append(Link(0, 1, 1, 1, 0))
        links.append(Link(1, 1, 2, 0, 0))
        links.append(Link(1, 0, 3, 0, 1))
        self._router = Router(links, False, 1024)

        self._nearest_ethernet_chip = (0, 0)

        self._ip = "192.162.240.253"

    def _create_processors(self, monitor=3, number=18):
        """ Create a list of processors.

        As some test change the processors this must be called each time.

        :param monitor: Id of process to make the monitor
        :type monitor: int
        """
        flops = 1000
        processors = list()
        for i in range(number):
            processors.append(Processor(i, flops, is_monitor=(i == monitor)))
        return processors

    def _create_chip(self, x, y, processors):
        if x == y == 0:
            return Chip(x, y, processors, self._router, self._sdram,
                        self._nearest_ethernet_chip[0],
                        self._nearest_ethernet_chip[1], self._ip)
        return Chip(x, y, processors, self._router, self._sdram,
                    self._nearest_ethernet_chip[0],
                    self._nearest_ethernet_chip[1], None)

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

        new_machine = machine_from_chips(chips)

        self.assertEqual(new_machine.max_chip_x, 4)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            if (c.x == c.y == 0):
                self.assertEqual(c.ip_address, self._ip)
            else:
                self.assertIsNone(c.ip_address)
            self.assertEqual(c.sdram, self._sdram)
            self.assertEqual(c.router, self._router)
            for p in processors:
                self.assertTrue(p in c.processors)

        self.assertEqual(new_machine.total_cores, 450)
        self.assertEqual(new_machine.total_available_user_cores, 425)
        self.assertEqual(new_machine.boot_chip.ip_address, self._ip)
        self.assertEqual(new_machine.n_chips, 25)
        self.assertEqual(len(new_machine), 25)
        self.assertEqual(next(x[1].ip_address for x in new_machine), self._ip)
        self.assertEqual(next(new_machine.chip_coordinates), (0, 0))
        self.assertEqual(new_machine.cores_and_link_output_string(),
                         "450 cores and 50.0 links")
        self.assertEqual(new_machine.__repr__(),
                         "[NoWrapMachine: max_x=4, max_y=4, n_chips=25]")
        self.assertEqual(list(new_machine.spinnaker_links), [])

    def test_create_new_machine_with_invalid_chips(self):
        """
        check that building a machine with invalid chips causes errors

        :rtype: None
        """
        chips = self._create_chips()
        chips.append(Chip(
            0, 0, self._create_processors(), self._router, self._sdram,
            self._nearest_ethernet_chip[0],
            self._nearest_ethernet_chip[1], self._ip))
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            machine_from_chips(chips)

    def test_machine_add_chip(self):
        """
        test the add_chip method of the machine object

        :rtype: None
        """
        processors = self._create_processors()
        new_machine = machine_from_size(6, 5, self._create_chips(processors))
        processor = list()
        processor.append(Processor(100, 100, False))
        extra_chip = self._create_chip(5, 0, processor)
        new_machine.add_chip(extra_chip)
        self.assertEqual(new_machine.max_chip_x, 5)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            if (c.x == c.y == 0):
                self.assertEqual(c.ip_address, self._ip)
            else:
                self.assertIsNone(c.ip_address)
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
        new_machine = machine_from_chips(chips)
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            new_machine.add_chip(chips[3])

    def test_machine_add_chips(self):
        """
        check that adding range of chips works

        :rtype: None
        """
        processors = self._create_processors()
        chips = self._create_chips(processors)
        new_machine = machine_from_size(6, 5, chips)

        extra_chips = list()
        extra_chips.append(self._create_chip(5, 0, processors))
        extra_chips.append(self._create_chip(5, 1, processors))
        extra_chips.append(self._create_chip(5, 2, processors))
        extra_chips.append(self._create_chip(5, 3, processors))

        new_machine.add_chips(extra_chips)
        self.assertEqual(new_machine.max_chip_x, 5)
        self.assertEqual(new_machine.max_chip_y, 4)

        for c in new_machine.chips:
            if (c.x == c.y == 0):
                self.assertEqual(c.ip_address, self._ip)
            else:
                self.assertIsNone(c.ip_address)
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
        new_machine = machine_from_size(7, 5, chips)

        processors = self._create_processors()
        extra_chips = list()
        extra_chips.append(self._create_chip(6, 0, processors))
        extra_chips.append(chips[3])

        with self.assertRaises(SpinnMachineAlreadyExistsException):
            new_machine.add_chips(extra_chips)

    def test_machine_get_chip_at(self):
        """
        test the get_chip_at function from the machine with a valid request

        :rtype: None
        """
        chips = self._create_chips()
        new_machine = machine_from_chips(chips)
        self.assertEqual(chips[0], new_machine.get_chip_at(0, 0))

    def test_machine_get_chip_at_invalid_location(self):
        """
        test the machines get_chip_at function with a location thats invalid,
        should return None and not produce an error

        :rtype: None
        """
        chips = self._create_chips()

        new_machine = machine_from_chips(chips)
        self.assertEqual(None, new_machine.get_chip_at(10, 0))

    def test_machine_is_chip_at_true(self):
        """
        test the is_chip_at function of the machine with a position to
        request which does indeed contain a chip

        :rtype: None
        """
        chips = self._create_chips()

        new_machine = machine_from_chips(chips)
        self.assertTrue(new_machine.is_chip_at(3, 0))

    def test_machine_is_chip_at_false(self):
        """
        test the is_chip_at function of the machine with a position to
        request which does not contain a chip

        :rtype: None
        """
        chips = self._create_chips()
        new_machine = machine_from_chips(chips)
        self.assertFalse(new_machine.is_chip_at(10, 0))

    def test_machine_get_chips_on_board(self):
        chips = self._create_chips()
        new_machine = machine_from_size(8, 8, chips)
        for eth_chip in new_machine._ethernet_connected_chips:
            chips_in_machine = list(
                new_machine.get_existing_xys_on_board(eth_chip))
            # _create_chips made a 5*5 grid of 25 chips,
            # but (0,4) is not on a standard 48-node board
            self.assertEqual(len(chips), 25)
            self.assertEqual(len(chips_in_machine), 24)
        self.assertIsNone(new_machine.get_spinnaker_link_with_id(1))
        self.assertIsNone(new_machine.get_fpga_link_with_id(1, 0))

    def test_x_y_over_link(self):
        """
        Test the x_y with each wrap around.

        Notice that the function only does the math not validate the values.
        :return:
        """
        # full wrap around
        machine = machine_from_size(24, 24)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (23, 23))
        self.assertEqual(machine.xy_over_link(23, 23, 1), (0, 0))
        # no wrap around'
        machine = machine_from_size(16, 16)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (-1, -1))
        self.assertEqual(machine.xy_over_link(15, 15, 1), (16, 16))
        # Horizontal wrap arounds
        machine = machine_from_size(24, 16)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (23, -1))
        self.assertEqual(machine.xy_over_link(23, 15, 1), (0, 16))
        # Vertical wrap arounds
        machine = machine_from_size(16, 24)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (-1, 23))
        self.assertEqual(machine.xy_over_link(15, 23, 1), (16, 0))


if __name__ == '__main__':
    unittest.main()
