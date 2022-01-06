# Copyright (c) 2021 The University of Manchester
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
from spinn_utilities.exceptions import (DataNotYetAvialable)
from spinn_machine import virtual_machine
from spinn_machine.config_setup import unittest_setup
from spinn_machine.data import MachineDataView
from spinn_machine.data.machine_data_writer import MachineDataWriter


class TestSimulatorData(unittest.TestCase):

    def setUp(cls):
        unittest_setup()

    def test_setup(self):
        view = MachineDataView()
        # What happens before setup depends on the previous test
        # Use manual_check to verify this without dependency
        writer = MachineDataWriter.setup()
        with self.assertRaises(DataNotYetAvialable):
            view.machine
        with self.assertRaises(DataNotYetAvialable):
            view.get_chip_at(1, 1)

    def test_mock(self):
        view = MachineDataView()
        MachineDataWriter.mock()
        self.assertEqual(3, view.get_chip_at(3, 5).x)
        self.assertEqual(48, view.machine.n_chips)

    def test_machine(self):
        view = MachineDataView()
        writer = MachineDataWriter.setup()
        with self.assertRaises(DataNotYetAvialable):
            view.machine
        self.assertFalse(view.has_machine())
        writer.set_machine(virtual_machine(width=2, height=2))
        self.assertEqual(4, view.machine.n_chips)
        self.assertEqual(1, view.get_chip_at(1, 0).x)
        self.assertIsNone(view.get_chip_at(4, 4))
        with self.assertRaises(TypeError):
            writer.set_machine("bacon")
        self.assertTrue(view.has_machine())
