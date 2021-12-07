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
        writer = MachineDataWriter()
        # What happens before setup depends on the previous test
        # Use manual_check to verify this without dependency
        writer.setup()
        with self.assertRaises(DataNotYetAvialable):
            view.machine

    def test_mock(self):
        view = MachineDataView()
        writer = MachineDataWriter()
        writer.mock()
        # check there is a
        #   value not what it is
        view.machine

    def test_machine(self):
        view = MachineDataView()
        writer = MachineDataWriter()
        writer.setup()
        with self.assertRaises(DataNotYetAvialable):
            view.machine
        self.assertFalse(view.has_machine())
        writer.set_machine(virtual_machine(width=2, height=2))
        self.assertEqual(4, view.machine.n_chips)
        with self.assertRaises(TypeError):
            writer.set_machine("bacon")
        self.assertTrue(view.has_machine())
