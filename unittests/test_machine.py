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
from spinn_machine.version import FIVE
from spinn_machine.version.version_strings import VersionStrings
from spinn_machine.virtual_machine import (
    virtual_machine_by_boards, virtual_machine_by_min_size)
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
        n_cores = MachineDataView.get_machine_version().max_cores_per_chip
        if x == y == 0:
            return Chip(x, y, n_cores, self._router, self._sdram,
                        self._nearest_ethernet_chip[0],
                        self._nearest_ethernet_chip[1], self._ip)
        return Chip(x, y, n_cores, self._router, self._sdram,
                    self._nearest_ethernet_chip[0],
                    self._nearest_ethernet_chip[1], None)

    def test_create_new_machine_version5(self):
        """
        test creating a new machine
        """
        # Tests the version 5 values specifically
        set_config("Machine", "version", FIVE)
        new_machine = virtual_machine_by_boards(1)

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
        # Strings hard coded to version 5
        set_config("Machine", "version", FIVE)
        machine = virtual_machine_by_boards(1)
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

    def test_chip_already_exists(self):
        """
        check that adding a chip that already exists causes an error

        :rtype: None
        """
        set_config("Machine", "versions", VersionStrings.ANY.value)
        machine = virtual_machine_by_boards(1)
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            machine.add_chip(Chip(
                0, 0, 18, self._router, self._sdram,
                self._nearest_ethernet_chip[0],
                self._nearest_ethernet_chip[1], self._ip))

    def test_machine_get_chip_at(self):
        """
        test the get_chip_at function from the machine with a valid request

        :rtype: None
        """
        set_config("Machine", "versions", VersionStrings.FOUR_PLUS.value)
        new_machine = virtual_machine_by_min_size(2, 2)
        self.assertEqual(1, new_machine.get_chip_at(1, 0).x)
        self.assertEqual(0, new_machine.get_chip_at(1, 0).y)
        self.assertEqual(0, new_machine.get_chip_at(0, 1).x)
        self.assertEqual(1, new_machine.get_chip_at(0, 1).y)

    def test_machine_big_x(self):
        """
        test the add_chips method of the machine chips outside size
        should produce an error

        :rtype: None
        """
        set_config("Machine", "versions", VersionStrings.ANY.value)
        version = MachineDataView.get_machine_version()
        width, height = version.board_shape
        # create an empty Machine
        machine = version.create_machine(width, height)
        machine.add_chip(self._create_chip(0, 0))
        # the add does not have the safety code
        machine.add_chip(self._create_chip(width + 2, height // 2))
        # however the validate does
        try:
            machine.validate()
        except SpinnMachineException as ex:
            self.assertIn(f"has an x larger than width {width}", str(ex))

    def test_machine_big_y(self):
        """
        test the add_chips method of the machine chips outside size
        should produce an error

        :rtype: None
        """
        set_config("Machine", "versions", VersionStrings.ANY.value)
        version = MachineDataView.get_machine_version()
        width, height = version.board_shape
        # create an empty Machine
        machine = version.create_machine(width, height)
        machine.add_chip(self._create_chip(0, 0))
        # the add does not have the safety code
        machine.add_chip(self._create_chip(width // 2, height + 2))
        # however the validate does
        try:
            machine.validate()
        except SpinnMachineException as ex:
            self.assertIn(f"has a y larger than height {height}", str(ex))

    def test_machine_get_chip_at_invalid_location(self):
        """
        test the machines get_chip_at function with a location thats invalid,
        should return None and not produce an error

        :rtype: None
        """
        set_config("Machine", "versions", VersionStrings.ANY.value)
        version = MachineDataView.get_machine_version()
        new_machine = virtual_machine_by_boards(1)
        width, height = version.board_shape
        self.assertEqual(None, new_machine.get_chip_at(width + 2, height // 2))

    def test_machine_is_chip_at_true(self):
        """
        test the is_chip_at function of the machine with a position to
        request which does indeed contain a chip

        :rtype: None
        """
        set_config("Machine", "versions", VersionStrings.ANY.value)
        version = MachineDataView.get_machine_version()
        new_machine = virtual_machine_by_boards(1)
        width, height = version.board_shape
        self.assertTrue(new_machine.is_chip_at(width // 2, height // 2))

    def test_machine_is_chip_at_false(self):
        """
        test the is_chip_at function of the machine with a position to
        request which does not contain a chip

        :rtype: None
        """
        set_config("Machine", "versions", VersionStrings.ANY.value)
        version = MachineDataView.get_machine_version()
        new_machine = virtual_machine_by_boards(1)
        width, height = version.board_shape
        self.assertFalse(new_machine.is_chip_at(width + 2, height // 2))

    def test_machine_get_chips_on_board(self):
        set_config("Machine", "versions", VersionStrings.MULTIPLE_BOARDS.value)
        new_machine = virtual_machine_by_boards(3)
        version = MachineDataView.get_machine_version()
        for eth_chip in new_machine._ethernet_connected_chips:
            chips_in_machine = list(
                new_machine.get_existing_xys_on_board(eth_chip))
            self.assertEqual(len(chips_in_machine), version.n_chips_per_board)
        # TODO use version info from other PR
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
        set_config("Machine", "versions", VersionStrings.WRAPPABLE.value)
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
        set_config("Machine", "versions", VersionStrings.WRAPPABLE.value)
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
        set_config("Machine", "versions", VersionStrings.ANY.value)
        version = MachineDataView.get_machine_version()
        width, height = version.board_shape
        # create an empty Machine
        machine = version.create_machine(width, height)
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_negative_x(self):
        set_config("Machine", "versions", VersionStrings.ANY.value)
        version = MachineDataView.get_machine_version()
        width, height = version.board_shape
        # create an empty Machine
        machine = version.create_machine(width, height)
        chip = self._create_chip(2, -1)
        machine.add_chip(chip)
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_negative_y(self):
        set_config("Machine", "versions", VersionStrings.ANY.value)
        version = MachineDataView.get_machine_version()
        width, height = version.board_shape
        # create an empty Machine
        machine = version.create_machine(width, height)
        chip = self._create_chip(-1, 3)
        machine.add_chip(chip)
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def _non_ethernet_chip(self, machine):
        for chip in machine.chips:
            if chip.ip_address is None:
                return chip
        raise SpinnMachineException("No none Ethernet Chip")

    def test_weird_ethernet1(self):
        set_config("Machine", "versions", VersionStrings.FOUR_PLUS.value)
        machine = virtual_machine_by_boards(1)
        self._non_ethernet_chip(machine)._ip_address = "1.2.3.4"
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_bad_ethernet_chip_x(self):
        set_config("Machine", "versions", VersionStrings.FOUR_PLUS.value)
        machine = virtual_machine_by_boards(1)
        width, _ = MachineDataView.get_machine_version().board_shape
        self._non_ethernet_chip(machine)._nearest_ethernet_x = width + 1
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_bad_ethernet_chip_no_chip(self):
        set_config("Machine", "versions", VersionStrings.FOUR_PLUS.value)
        machine = virtual_machine_by_boards(1)
        _, height = MachineDataView.get_machine_version().board_shape
        self._non_ethernet_chip(machine)._nearest_ethernet_x = height + 1
        with self.assertRaises(SpinnMachineException):
            machine.validate()

    def test_concentric_xys(self):
        set_config("Machine", "versions", VersionStrings.BIG.value)
        machine = virtual_machine_by_min_size(5, 5)
        found = list(machine.concentric_xys(2, (2, 2)))
        expected = [
            (2, 2),
            (2, 1), (3, 2), (3, 3), (2, 3), (1, 2), (1, 1),
            (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (3, 4),
            (2, 4), (1, 3), (0, 2), (0, 1), (0, 0), (1, 0)]
        self.assertListEqual(expected, found)

    def test_too_few_cores(self):
        set_config("Machine", "versions", VersionStrings.ANY.value)
        machine = virtual_machine_by_boards(1)
        # Hack to get n_processors return a low number
        chip = next(machine.chips)
        chip._placable_processors = tuple([1, 2])
        with self.assertRaises(SpinnMachineException):
            machine.validate()


if __name__ == '__main__':
    unittest.main()
