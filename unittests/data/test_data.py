# Copyright (c) 2021-2022 The University of Manchester
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

import unittest
from spinn_utilities.exceptions import (
    DataNotYetAvialable, UnexpectedStateChange)
from spinn_machine import virtual_machine
from spinn_machine.config_setup import unittest_setup
from spinn_machine.data import MachineDataView
from spinn_machine.data.machine_data_writer import MachineDataWriter


class TestSimulatorData(unittest.TestCase):

    def setUp(cls):
        unittest_setup()

    def test_setup(self):
        # What happens before setup depends on the previous test
        # Use manual_check to verify this without dependency
        MachineDataWriter.setup()
        with self.assertRaises(DataNotYetAvialable):
            MachineDataView.get_machine()
        with self.assertRaises(DataNotYetAvialable):
            MachineDataView.get_chip_at(1, 1)

    def test_mock(self):
        MachineDataWriter.mock()
        self.assertEqual(3, MachineDataView.get_chip_at(3, 5).x)
        self.assertEqual(48, MachineDataView.get_machine().n_chips)

    def test_reset_fixed(self):
        writer = MachineDataWriter.setup()
        writer.set_machine(virtual_machine(2, 2), True)
        machine1 = MachineDataView.get_machine()
        self.assertFalse(writer.get_user_accessed_machine())
        writer.start_run()
        writer.finish_run()
        # Without a reset the machine starts the same
        machine2 = MachineDataView.get_machine()
        self.assertEqual(id(machine1), id(machine2))
        # After get machine the reset is hard on if not fixed
        writer.soft_reset()
        self.assertTrue(MachineDataView.is_soft_reset())
        machine3 = MachineDataView.get_machine()
        self.assertEqual(id(machine1), id(machine3))

    def test_reset_not_fixed(self):
        writer = MachineDataWriter.setup()
        writer.set_machine(virtual_machine(2, 2), False)
        self.assertFalse(writer.get_user_accessed_machine())
        machine1 = MachineDataView.get_machine()
        self.assertTrue(writer.get_user_accessed_machine())
        writer.start_run()
        writer.finish_run()
        # Without a reset the machine starts the same
        machine2 = MachineDataView.get_machine()
        self.assertEqual(id(machine1), id(machine2))
        # After get machine soft reset not allowed
        with self.assertRaises(UnexpectedStateChange):
            writer.soft_reset()
        # A hard reset is. ASB picks the right one
        writer.hard_reset()
        with self.assertRaises(DataNotYetAvialable):
            MachineDataView.get_machine()

    def test_reset_not_fixed_hacked(self):
        writer = MachineDataWriter.setup()
        writer.set_machine(virtual_machine(2, 2), False)
        # hack to get machine without it being known it was accessed
        machine1 = writer._MachineDataWriter__data._machine
        # Due to hack access to machine this is still False
        self.assertFalse(writer.get_user_accessed_machine())
        writer.start_run()
        writer.finish_run()
        # Without a reset the machine starts the same
        machine2 = writer._MachineDataWriter__data._machine
        self.assertEqual(id(machine1), id(machine2))
        # user has not access machine so can be soft
        writer.soft_reset()
        self.assertTrue(MachineDataView.is_soft_reset())
        machine3 = writer._MachineDataWriter__data._machine
        self.assertEqual(id(machine1), id(machine3))
        with self.assertRaises(DataNotYetAvialable):
            MachineDataView.get_machine()

    def test_machine(self):
        writer = MachineDataWriter.setup()
        with self.assertRaises(DataNotYetAvialable):
            MachineDataView.get_machine()
        self.assertFalse(MachineDataWriter.has_machine())
        writer.set_machine(virtual_machine(width=2, height=2))
        self.assertEqual(4, MachineDataView.get_machine().n_chips)
        self.assertEqual(1, MachineDataView.get_chip_at(1, 0).x)
        with self.assertRaises(KeyError):
            MachineDataView.get_chip_at(4, 4)
        with self.assertRaises(TypeError):
            writer.set_machine("bacon")
        self.assertTrue(MachineDataView.has_machine())

    def test_where_is_mocked(self):
        writer = MachineDataWriter.mock()
        self.assertEqual(
            "No Machine created yet",
            MachineDataView.where_is_xy(1, 0))
        self.assertEqual(
            "No Machine created yet",
            MachineDataView.where_is_xy(11, 11))
        machine = virtual_machine(width=12, height=12)
        writer.set_machine(machine)
        self.assertEqual(
            "global chip 11, 11 on 127.0.0.0 is chip 7, 3 on 127.0.4.8",
            MachineDataView.where_is_xy(11, 11))
        self.assertEqual(
            "global chip 2, 8 on 127.0.0.0 is chip 6, 4 on 127.0.8.4",
            MachineDataView.where_is_chip(machine.get_chip_at(2, 8)))

    def test_where_is_setup(self):
        writer = MachineDataWriter.setup()
        self.assertEqual(
            "No Machine created yet",
            MachineDataView.where_is_xy(1, 0))
        writer.set_machine(virtual_machine(width=12, height=12))
        self.assertEqual(
            "global chip 11, 11 on 127.0.0.0 is chip 7, 3 on 127.0.4.8",
            MachineDataView.where_is_xy(11, 11))
        self.assertEqual(
            "No chip -1, 11 found",
            MachineDataView.where_is_xy(-1, 11))
