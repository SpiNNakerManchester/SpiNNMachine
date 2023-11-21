# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
test for testing the python representation of a spinnaker machine
"""
from testfixtures import LogCapture
import unittest
from spinn_utilities.config_holder import set_config
from spinn_utilities.testing import log_checker
from spinn_machine import Link, Router, Chip
from spinn_machine import virtual_machine
from spinn_machine.config_setup import unittest_setup
from spinn_machine.data import MachineDataView
from spinn_machine.exceptions import (
    SpinnMachineAlreadyExistsException, SpinnMachineException)


class SpinnMachineTestCase(unittest.TestCase):
    """
    test for testing the python representation of a spinnaker machine
    """

    def setUp(self):
        unittest_setup()
        set_config("Machine", "version", 5)

        self._sdram = 123469792

        links = list()
        links.append(Link(0, 0, 0, 1, 1))
        links.append(Link(0, 1, 1, 1, 0))
        links.append(Link(1, 1, 2, 0, 0))
        links.append(Link(1, 0, 3, 0, 1))
        self._router = Router(links, 1024)

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

    def test_create_new_machine(self):
        """
        test creating a new machine
        """
        new_machine = virtual_machine(8, 8)

        self.assertEqual(new_machine.width, 8)
        self.assertEqual(new_machine.height, 8)

        for c in new_machine.chips:
            if (c.x == c.y == 0):
                self.assertEqual(c.ip_address, "127.0.0.0")
            else:
                self.assertIsNone(c.ip_address)
            self.assertEqual(123469792, c.sdram)
            self.assertIsNotNone(c.router)

        self.assertEqual(new_machine.total_cores, 856)
        self.assertEqual(new_machine.total_available_user_cores, 856 - 48)
        self.assertEqual(new_machine.boot_chip.ip_address, "127.0.0.0")
        self.assertEqual(new_machine.n_chips, 48)
        self.assertEqual(len(new_machine), 48)
        self.assertEqual(
            next(x[1].ip_address for x in new_machine), "127.0.0.0")
        self.assertEqual(next(new_machine.chip_coordinates), (0, 0))
        self.assertEqual(
            "[VirtualNoWrapMachine: width=8, height=8, n_chips=48]",
            new_machine.__repr__())
        self.assertEqual(2, len(list(new_machine.spinnaker_links)))
        self.assertEqual(1023, new_machine.min_n_router_enteries)

    def test_summary(self):
        machine = virtual_machine(8, 8)
        self.assertEqual(
            "Machine on 127.0.0.0 with 48 Chips, 856 cores and 120.0 links. "
            "Chips have sdram of 123469792 bytes, router table of size 1023, "
            "between 17 and 18 cores and between 3 and 6 links.",
            machine.summary_string())

        # Hack to test sefety code. Doing this outside tests not supported
        machine._sdram_counter.clear()
        machine._sdram_counter[123] += 1
        machine._n_router_entries_counter.clear()
        machine._n_router_entries_counter[456] += 1
        with LogCapture() as lc:
            self.assertEqual(
                "Machine on 127.0.0.0 with 48 Chips, 856 cores and 120.0"
                " links. Chips have sdram of 123 bytes, router table of size "
                "456, between 17 and 18 cores and between 3 and 6 links.",
                machine.summary_string())
            log_checker.assert_logs_warning_contains(
                lc.records,
                "The sdram per chip of 123 was different to the expected "
                "value of 123469792 for board Version Spin1 48 Chip")
            log_checker.assert_logs_warning_contains(
                lc.records,
                "The number of router entries per chip of 456 was different "
                "to the expected value of 1023 "
                "for board Version Spin1 48 Chip")

        # Hack to test sefety code. Doing this outside tests not supported
        machine._sdram_counter[789] += 1
        machine._n_router_entries_counter[321] += 1
        with LogCapture() as lc:
            self.assertEqual(
                "Machine on 127.0.0.0 with 48 Chips, 856 cores and 120.0 "
                "links. Chips have sdram of between 123 and 789 bytes, "
                "router table sizes between 321 and 456, "
                "between 17 and 18 cores and between 3 and 6 links.",
                machine.summary_string())
            log_checker.assert_logs_warning_contains(
                lc.records,
                "Not all Chips have the same sdram. "
                "The counts where Counter({123: 1, 789: 1}).")
            log_checker.assert_logs_warning_contains(
                lc.records,
                "Not all Chips had the same n_router_tables. "
                "The counts where Counter({456: 1, 321: 1}).")

    def test_create_new_machine_with_invalid_chips(self):
        """
        check that building a machine with invalid chips causes errors

        :rtype: None
        """
        machine = virtual_machine(8, 8)
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            machine.add_chip(Chip(
                0, 0, 18, self._router, self._sdram,
                self._nearest_ethernet_chip[0],
                self._nearest_ethernet_chip[1], self._ip))

    def test_machine_add_chip(self):
        """
        test the add_chip method of the machine object

        :rtype: None
        """
        new_machine = virtual_machine(8, 8)
        extra_chip = self._create_chip(5, 0)
        new_machine.add_chip(extra_chip)

        for c in new_machine.chips:
            if (c.x == c.y == 0):
                self.assertEqual(c.ip_address, "127.0.0.0")
            else:
                self.assertIsNone(c.ip_address)
            self.assertEqual(c.sdram, self._sdram)
            self.assertIsNotNone(c.router)

    def test_machine_add_duplicate_chip(self):
        """
        test if adding the same chip twice causes an error

        :rtype: None
        """
        new_machine = virtual_machine(8, 8)
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            new_machine.add_chip(new_machine.get_chip_at(1, 1))

    def test_machine_get_chip_at(self):
        """
        test the get_chip_at function from the machine with a valid request

        :rtype: None
        """
        new_machine = virtual_machine(8, 8)
        self.assertEqual(2, new_machine.get_chip_at(2, 3).x)
        self.assertEqual(3, new_machine.get_chip_at(2, 3).y)

    def test_machine_big_x(self):
        """
        test the add_chips method of the machine chips outside size
        should produce an error

        :rtype: None
        """
        machine = MachineDataView.get_machine_version().create_machine(8, 8)
        machine.add_chip(self._create_chip(0, 0))
        # the add does not have the safety code
        machine.add_chip(self._create_chip(10, 2))
        # however the validate does
        try:
            machine.validate()
        except SpinnMachineException as ex:
            self.assertIn("has an x larger than width 8", str(ex))

    def test_machine_big_y(self):
        """
        test the add_chips method of the machine chips outside size
        should produce an error

        :rtype: None
        """
        version = MachineDataView.get_machine_version()
        new_machine = version.create_machine(8, 8)
        new_machine.add_chip(self._create_chip(0, 0))
        # the add does not have the safety code
        new_machine.add_chip(self._create_chip(2, 10))
        # however the validate does
        try:
            new_machine.validate()
        except SpinnMachineException as ex:
            self.assertIn("has a y larger than height 8", str(ex))

    def test_machine_get_chip_at_invalid_location(self):
        """
        test the machines get_chip_at function with a location thats invalid,
        should return None and not produce an error

        :rtype: None
        """
        new_machine = virtual_machine(8, 8)
        self.assertEqual(None, new_machine.get_chip_at(10, 0))

    def test_machine_is_chip_at_true(self):
        """
        test the is_chip_at function of the machine with a position to
        request which does indeed contain a chip

        :rtype: None
        """
        new_machine = virtual_machine(8, 8)
        self.assertTrue(new_machine.is_chip_at(3, 0))

    def test_machine_is_chip_at_false(self):
        """
        test the is_chip_at function of the machine with a position to
        request which does not contain a chip

        :rtype: None
        """
        new_machine = virtual_machine(8, 8)
        self.assertFalse(new_machine.is_chip_at(10, 0))

    def test_machine_get_chips_on_board(self):
        new_machine = virtual_machine(8, 8)
        for eth_chip in new_machine._ethernet_connected_chips:
            chips_in_machine = list(
                new_machine.get_existing_xys_on_board(eth_chip))
            # _create_chips made a 5*5 grid of 25 chips,
            # but (0,4) is not on a standard 48-node board
            self.assertEqual(len(chips_in_machine), 48)
        with self.assertRaises(KeyError):
            new_machine.get_spinnaker_link_with_id(1)
        with self.assertRaises(KeyError):
            new_machine.get_fpga_link_with_id(3, 3)

    def test_x_y_over_link(self):
        """
        Test the x_y with each wrap around.

        Notice that the function only does the math not validate the values.
        :return:
        """
        # full wrap around
        machine = MachineDataView.get_machine_version().create_machine(24, 24)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (23, 23))
        self.assertEqual(machine.xy_over_link(23, 23, 1), (0, 0))
        self.assertEqual(machine.wrap, "Wrapped")
        # no wrap around'
        machine = MachineDataView.get_machine_version().create_machine(16, 16)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (-1, -1))
        self.assertEqual(machine.xy_over_link(15, 15, 1), (16, 16))
        self.assertEqual(machine.wrap, "NoWrap")
        # Horizontal wrap arounds
        machine = MachineDataView.get_machine_version().create_machine(24, 16)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (23, -1))
        self.assertEqual(machine.xy_over_link(23, 15, 1), (0, 16))
        self.assertEqual(machine.wrap, "HorWrap")
        # Vertical wrap arounds
        machine = MachineDataView.get_machine_version().create_machine(16, 24)
        self.assertEqual(machine.xy_over_link(0, 0, 4), (-1, 23))
        self.assertEqual(machine.xy_over_link(15, 23, 1), (16, 0))
        self.assertEqual(machine.wrap, "VerWrap")

    def test_get_global_xy(self):
        """
        Test get_global_xy with each wrap around.

        Notice that the function only does the math not validate the values.
        :return:
        """
        # full wrap around
        machine = MachineDataView.get_machine_version().create_machine(24, 24)
        self.assertEqual(machine.get_global_xy(1, 4, 4, 20), (5, 0))
        self.assertEqual(machine.get_global_xy(5, 0, 20, 4), (1, 4))
        # no wrap around'
        machine = MachineDataView.get_machine_version().create_machine(28, 28)
        self.assertEqual(machine.get_global_xy(1, 4, 4, 20), (5, 24))
        self.assertEqual(machine.get_global_xy(5, 0, 20, 4), (25, 4))
        # Horizontal wrap arounds
        machine = MachineDataView.get_machine_version().create_machine(24, 28)
        self.assertEqual(machine.get_global_xy(1, 4, 4, 20), (5, 24))
        self.assertEqual(machine.get_global_xy(5, 0, 20, 4), (1, 4))
        # Vertical wrap arounds
        machine = MachineDataView.get_machine_version().create_machine(28, 24)
        self.assertEqual(machine.get_global_xy(1, 4, 4, 20), (5, 0))
        self.assertEqual(machine.get_global_xy(5, 0, 20, 4), (25, 4))

    def test_no_boot(self):
        machine = MachineDataView.get_machine_version().create_machine(8, 8)
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_negative_x(self):
        machine = MachineDataView.get_machine_version().create_machine(8, 8)
        chip = self._create_chip(2, -1)
        machine.add_chip(chip)
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_negative_y(self):
        machine = MachineDataView.get_machine_version().create_machine(8, 8)
        chip = self._create_chip(-1, 3)
        machine.add_chip(chip)
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_big_x(self):
        machine = virtual_machine(8, 8)
        machine.get_chip_at(1, 1)._x = 9
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_big_y(self):
        machine = virtual_machine(8, 8)
        machine.get_chip_at(1, 1)._y = 9
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_weird_ethernet1(self):
        machine = virtual_machine(8, 8)
        machine.get_chip_at(1, 3)._ip_address = "1.2.3.4"
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_bad_ethernet_chip_x(self):
        machine = virtual_machine(8, 8)
        machine.get_chip_at(0, 1)._nearest_ethernet_x = 1
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_bad_ethernet_chip_no_chip(self):
        machine = virtual_machine(8, 8)
        machine.get_chip_at(0, 1)._nearest_ethernet_x = 12
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_getitem(self):
        machine = virtual_machine(8, 8)
        chip12 = machine[(1, 2)]
        self.assertEqual(chip12.x, 1)
        self.assertEqual(chip12.y, 2)
        self.assertTrue((1, 2) in machine)
        self.assertFalse((1, 9) in machine)

    def test_concentric_xys(self):
        machine = virtual_machine(8, 8)
        machine.get_chip_at(1, 3)
        found = list(machine.concentric_xys(2, (2, 2)))
        expected = [
            (2, 2),
            (2, 1), (3, 2), (3, 3), (2, 3), (1, 2), (1, 1),
            (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (3, 4),
            (2, 4), (1, 3), (0, 2), (0, 1), (0, 0), (1, 0)]
        self.assertListEqual(expected, found)

    def test_too_few_cores(self):
        machine = virtual_machine(8, 8)
        # Hack to get n_processors return a low number
        machine.get_chip_at(0, 1)._p = [1, 2, 3]
        with self.assertRaises(SpinnMachineException):
            machine.validate()


if __name__ == '__main__':
    unittest.main()
