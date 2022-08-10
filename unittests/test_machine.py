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
from unittest import SkipTest
from spinn_machine import (
    Link, SDRAM, Router, Chip, Machine, machine_from_chips, machine_from_size)
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import (
    SpinnMachineAlreadyExistsException, SpinnMachineException)


class SpinnMachineTestCase(unittest.TestCase):
    """
    test for testing the python representation of a spinnaker machine
    """

    def setUp(self):
        unittest_setup()
        self._sdram = SDRAM(128)

        links = list()
        links.append(Link(0, 0, 0, 1, 1))
        links.append(Link(0, 1, 1, 1, 0))
        links.append(Link(1, 1, 2, 0, 0))
        links.append(Link(1, 0, 3, 0, 1))
        self._router = Router(links, False, 1024)

        self._nearest_ethernet_chip = (0, 0)

        self._ip = "192.162.240.253"

    def _create_chip(self, x, y):
        if x == y == 0:
            return Chip(x, y, 18, self._router, self._sdram,
                        self._nearest_ethernet_chip[0],
                        self._nearest_ethernet_chip[1], self._ip)
        return Chip(x, y, 18, self._router, self._sdram,
                    self._nearest_ethernet_chip[0],
                    self._nearest_ethernet_chip[1], None)

    def _create_chips(self):
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(self._create_chip(x, y))
        return chips

    def test_create_new_machine(self):
        """
        test creating a new machine
        """
        chips = self._create_chips()

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
            0, 0, 18, self._router, self._sdram,
            self._nearest_ethernet_chip[0],
            self._nearest_ethernet_chip[1], self._ip))
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            machine_from_chips(chips)

    def test_machine_add_chip(self):
        """
        test the add_chip method of the machine object

        :rtype: None
        """
        new_machine = machine_from_size(6, 5, self._create_chips())
        extra_chip = self._create_chip(5, 0)
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
        chips = self._create_chips()
        new_machine = machine_from_size(6, 5, chips)

        extra_chips = list()
        extra_chips.append(self._create_chip(5, 0))
        extra_chips.append(self._create_chip(5, 1))
        extra_chips.append(self._create_chip(5, 2))
        extra_chips.append(self._create_chip(5, 3))

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

    def test_machine_add_duplicate_chips(self):
        """
        test the add_chips method of the machine with duplicate chips.
        should produce an error

        :rtype: None
        """
        chips = self._create_chips()
        new_machine = machine_from_size(7, 5, chips)

        extra_chips = list()
        extra_chips.append(self._create_chip(6, 0))
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
        self.assertEquals(machine.wrap, "Wrapped")
        # no wrap around'
        machine = machine_from_size(16, 16)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (-1, -1))
        self.assertEqual(machine.xy_over_link(15, 15, 1), (16, 16))
        self.assertEquals(machine.wrap, "NoWrap")
        # Horizontal wrap arounds
        machine = machine_from_size(24, 16)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (23, -1))
        self.assertEqual(machine.xy_over_link(23, 15, 1), (0, 16))
        self.assertEquals(machine.wrap, "HorWrap")
        # Vertical wrap arounds
        machine = machine_from_size(16, 24)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (-1, 23))
        self.assertEqual(machine.xy_over_link(15, 23, 1), (16, 0))
        self.assertEquals(machine.wrap, "VerWrap")

    def test_get_global_xy(self):
        """
        Test get_global_xy with each wrap around.

        Notice that the function only does the math not validate the values.
        :return:
        """
        # full wrap around
        machine = machine_from_size(24, 24)
        self.assertEqual(machine.get_global_xy(1, 4, 4, 20), (5, 0))
        self.assertEqual(machine.get_global_xy(5, 0, 20, 4), (1, 4))
        # no wrap around'
        machine = machine_from_size(28, 28)
        self.assertEqual(machine.get_global_xy(1, 4, 4, 20), (5, 24))
        self.assertEqual(machine.get_global_xy(5, 0, 20, 4), (25, 4))
        # Horizontal wrap arounds
        machine = machine_from_size(24, 28)
        self.assertEqual(machine.get_global_xy(1, 4, 4, 20), (5, 24))
        self.assertEqual(machine.get_global_xy(5, 0, 20, 4), (1, 4))
        # Vertical wrap arounds
        machine = machine_from_size(28, 24)
        self.assertEqual(machine.get_global_xy(1, 4, 4, 20), (5, 0))
        self.assertEqual(machine.get_global_xy(5, 0, 20, 4), (25, 4))

    def test_max_cores_per_chip(self):
        """
        Test set_max_cores_per_chip

        Note: Method tested here may not be
        :return:
        """
        Machine.set_max_cores_per_chip(10)
        self.assertEqual(Machine.max_cores_per_chip(), 10)
        with self.assertRaises(SpinnMachineException):
            Machine.set_max_cores_per_chip(11)
        # hack to set back to None to not break other tests
        Machine._Machine__max_cores = None
        self.assertEqual(Machine.max_cores_per_chip(), 18)

    def test_no_boot(self):
        machine = machine_from_size(8, 8)
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_negative_x(self):
        chips = self._create_chips()
        chips[3]._x = -1
        machine = machine_from_chips(chips)
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_negative_y(self):
        chips = self._create_chips()
        chips[3]._y = -1
        machine = machine_from_chips(chips)
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_big_x(self):
        chips = self._create_chips()
        machine = machine_from_chips(chips)
        chips[3]._x = 9
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_big_y(self):
        chips = self._create_chips()
        machine = machine_from_chips(chips)
        chips[3]._y = 9
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_weird_ethernet1(self):
        chips = self._create_chips()
        machine = machine_from_chips(chips)
        # chips[8] = x;1 y3
        chips[8]._ip_address = "1.2.3.4"
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_weird_ethernet2(self):
        chips = self._create_chips()
        machine = machine_from_chips(chips)
        # chips[1] = x:0 y:1
        chips[1]._ip_address = "1.2.3.4"
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_bad_ethernet_chip_x(self):
        chips = self._create_chips()
        machine = machine_from_chips(chips)
        # chips[1] = x:0 y:1
        chips[1]._nearest_ethernet_x = 1
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_bad_ethernet_chip_no_chip(self):
        chips = self._create_chips()
        machine = machine_from_chips(chips)
        # chips[1] = x:0 y:1
        chips[1]._nearest_ethernet_x = 12
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_getitem(self):
        chips = self._create_chips()
        machine = machine_from_chips(chips)
        chip12 = machine[(1, 2)]
        self.assertEqual(chip12.x, 1)
        self.assertEqual(chip12.y, 2)
        self.assertTrue((1, 2) in machine)
        self.assertFalse((1, 9) in machine)

    def test_concentric_xys(self):
        chips = self._create_chips()
        machine = machine_from_chips(chips)
        found = list(machine.concentric_xys(2, (2, 2)))
        expected = [
            (2, 2),
            (2, 1), (3, 2), (3, 3), (2, 3), (1, 2), (1, 1),
            (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (3, 4),
            (2, 4), (1, 3), (0, 2), (0, 1), (0, 0), (1, 0)]
        self.assertListEqual(expected, found)


if __name__ == '__main__':
    unittest.main()
