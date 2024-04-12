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
from spinn_machine.version import FIVE, THREE
from spinn_machine.version.version_strings import VersionStrings


class TestSimulatorData(unittest.TestCase):

    def setUp(self):
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
        set_config("Machine", "version", FIVE)
        self.assertEqual(3, MachineDataView.get_chip_at(3, 5).x)
        self.assertEqual(48, MachineDataView.get_machine().n_chips)

    def test_machine(self):
        set_config("Machine", "version", THREE)
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
        set_config("Machine", "versions", VersionStrings.MULTIPLE_BOARDS.value)
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
        set_config("Machine", "versions", VersionStrings.MULTIPLE_BOARDS.value)
        writer = MachineDataWriter.setup()
        self.assertEqual(
            "No Machine created yet",
            MachineDataView.where_is_xy(1, 0))
        machine = virtual_machine(width=12, height=12)
        writer.set_machine(machine)
        self.assertEqual(
            "global chip 11, 11 on 127.0.0.0 is chip 7, 3 on 127.0.4.8",
            MachineDataView.where_is_xy(11, 11))
        self.assertEqual(
            "No chip -1, 11 found",
            MachineDataView.where_is_xy(-1, 11))
        self.assertEqual(
            "global chip 2, 8 on 127.0.0.0 is chip 6, 4 on 127.0.8.4",
            MachineDataView.where_is_chip(machine.get_chip_at(2, 8)))
        self.assertEqual(
            "None",
            MachineDataView.where_is_chip(None)
        )

    def test_mock_any(self):
        # Should work with any version
        set_config("Machine", "versions", VersionStrings.ANY.value)
        # check there is a value not what it is
        machine = MachineDataView.get_machine()
        self.assertGreaterEqual(machine.n_chips, 1)

    def test_mock_4_or_more(self):
        # Should work with any version
        set_config("Machine", "versions", VersionStrings.FOUR_PLUS.value)
        # check there is a value not what it is
        machine = MachineDataView.get_machine()
        self.assertGreaterEqual(machine.n_chips, 4)

    def test_mock_big(self):
        # Should work with any version
        set_config("Machine", "versions", VersionStrings.BIG.value)
        # check there is a value not what it is
        machine = MachineDataView.get_machine()
        self.assertGreaterEqual(machine.n_chips, 48)

    def test_mock3(self):
        # Should work with any version
        set_config("Machine", "version", 3)
        # check there is a value not what it is
        MachineDataView.get_machine()

    def test_mock5(self):
        set_config("Machine", "version", 5)
        # check there is a value not what it is
        MachineDataView.get_machine()

    def test_mock201(self):
        set_config("Machine", "version", 201)
        # check there is a value not what it is
        MachineDataView.get_machine()

    def test_get_monitors(self):
        writer = MachineDataWriter.setup()
        self.assertEqual(0, MachineDataView.get_all_monitor_cores())
        self.assertEqual(0, MachineDataView.get_ethernet_monitor_cores())
        writer.add_monitor_core(True)
        self.assertEqual(1, MachineDataView.get_all_monitor_cores())
        self.assertEqual(1, MachineDataView.get_ethernet_monitor_cores())
        writer.add_monitor_core(False)
        writer.add_monitor_core(True)
        self.assertEqual(2, MachineDataView.get_all_monitor_cores())
        self.assertEqual(3, MachineDataView.get_ethernet_monitor_cores())
