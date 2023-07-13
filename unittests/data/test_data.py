# Copyright (c) 2021 The University of Manchester
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

import unittest
from spinn_utilities.config_holder import set_config
from spinn_utilities.exceptions import (DataNotYetAvialable)
from spinn_machine import virtual_machine
from spinn_machine.config_setup import unittest_setup
from spinn_machine.data import MachineDataView
from spinn_machine.data.machine_data_writer import MachineDataWriter


class TestSimulatorData(unittest.TestCase):

    def setUp(cls):
        unittest_setup()
        set_config("Machine", "version", 5)

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

    def test_machine(self):
        set_config("Machine", "version", 3)
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
