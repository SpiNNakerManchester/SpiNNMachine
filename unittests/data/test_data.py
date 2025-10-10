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
from spinn_utilities.exceptions import (ConfigException, DataNotYetAvialable)
from spinn_machine import virtual_machine
from spinn_machine.config_setup import unittest_setup
from spinn_machine.data import MachineDataView
from spinn_machine.data.machine_data_writer import MachineDataWriter
from spinn_machine.exceptions import SpinnMachineException
from spinn_machine.version import FIVE, THREE, SPIN2_48CHIP
from spinn_machine.version.version_strings import VersionStrings


class TestSimulatorData(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_setup(self) -> None:
        # What happens before setup depends on the previous test
        # Use manual_check to verify this without dependency
        MachineDataWriter.setup()
        with self.assertRaises(DataNotYetAvialable):
            MachineDataView.get_machine()
        with self.assertRaises(DataNotYetAvialable):
            MachineDataView.get_chip_at(1, 1)

    def test_mock(self) -> None:
        set_config("Machine", "version", str(FIVE))
        self.assertEqual(3, MachineDataView.get_chip_at(3, 5).x)
        self.assertEqual(48, MachineDataView.get_machine().n_chips)

    def test_machine(self) -> None:
        set_config("Machine", "version", str(THREE))
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
            writer.set_machine("bacon")  # type: ignore[arg-type]
        self.assertTrue(MachineDataView.has_machine())

    def test_where_is_mocked(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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
            MachineDataView.where_is_chip(machine[2, 8]))

    def test_where_is_setup(self) -> None:
        set_config("Machine", "versions", VersionStrings.BIG.text)
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
            MachineDataView.where_is_chip(machine[2, 8]))
        self.assertEqual(
            "None",
            MachineDataView.where_is_chip(None)  # type: ignore[arg-type]
        )

    def test_v_to_p_spin1(self) -> None:
        writer = MachineDataWriter.setup()
        set_config("Machine", "version", str(FIVE))
        # Before setting
        with self.assertRaises(DataNotYetAvialable):
            writer.get_physical_core_id((1, 2), 3)
        self.assertEqual("", writer.get_physical_string((1, 2), 3))

        # Set a v_to_p
        v_to_p = dict()
        v_to_p[(1, 2)] = bytes([10, 11, 12, 13, 14])
        writer.set_v_to_p_map(v_to_p)
        # XY that exists
        self.assertEqual(13, writer.get_physical_core_id((1, 2), 3))
        self.assertEqual(" (ph: 13)",
                         writer.get_physical_string((1, 2), 3))
        # Xy that does not exist
        with self.assertRaises(KeyError):
            writer.get_physical_core_id((1, 4), 3)
        self.assertEqual("",
                         writer.get_physical_string((1, 4), 3))
        with self.assertRaises(IndexError):
            writer.get_physical_core_id((1, 2), 19)
        self.assertEqual("",
                         writer.get_physical_string((1, 2), 19))

    def test_v_to_p_spin2(self) -> None:
        writer = MachineDataWriter.setup()
        set_config("Machine", "version", str(SPIN2_48CHIP))

        # exists
        self.assertEqual((7, 6, 2), writer.get_physical_quad(3))
        self.assertEqual(" (qpe:7, 6, 2)",
                         writer.get_physical_string((1, 2), 3))
        with self.assertRaises(KeyError):
            writer.get_physical_quad(234)
        self.assertEqual("",
                         writer.get_physical_string((1, 2), 234))

    def test_mock_any(self) -> None:
        # Should work with any version
        set_config("Machine", "versions", VersionStrings.ANY.text)
        # check there is a value not what it is
        machine = MachineDataView.get_machine()
        self.assertGreaterEqual(machine.n_chips, 1)

    def test_mock_4_or_more(self) -> None:
        # Should work with any version that has 4 plus Chips
        set_config("Machine", "versions", VersionStrings.FOUR_PLUS.text)
        # check there is a value not what it is
        machine = MachineDataView.get_machine()
        self.assertGreaterEqual(machine.n_chips, 4)

    def test_mock_big(self) -> None:
        # Should work with any version
        set_config("Machine", "versions", VersionStrings.BIG.text)
        # check there is a value not what it is
        machine = MachineDataView.get_machine()
        self.assertGreaterEqual(machine.n_chips, 48)

    def test_mock3(self) -> None:
        # Should work with any version
        set_config("Machine", "version", "3")
        # check there is a value not what it is
        MachineDataView.get_machine()

    def test_mock5(self) -> None:
        set_config("Machine", "version", "5")
        # check there is a value not what it is
        MachineDataView.get_machine()

    def test_mock201(self) -> None:
        set_config("Machine", "version", "201")
        # check there is a value not what it is
        MachineDataView.get_machine()

    def test_get_monitors(self) -> None:
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

    def test_no_version(self) -> None:
        set_config("Machine", "machine_name", "SpiNNaker1M")
        try:
            MachineDataView.get_machine_version()
            raise ConfigException("Should not get here")
        except SpinnMachineException as ex:
            msg = str(ex)
            self.assertIn("SpiNNaker1M", msg)

    def test_required(self) -> None:
        writer = MachineDataWriter.setup()
        with self.assertRaises(DataNotYetAvialable):
            self.assertIsNone(MachineDataView.get_n_boards_required())
        self.assertFalse(MachineDataView.has_n_boards_required())
        with self.assertRaises(DataNotYetAvialable):
            self.assertIsNone(MachineDataView.get_n_chips_needed())
        self.assertFalse(MachineDataView.has_n_chips_needed())

        # required higher than in graph
        writer.set_n_required(None, 20)
        self.assertFalse(MachineDataView.has_n_boards_required())
        self.assertEqual(20, MachineDataView.get_n_chips_needed())
        writer.set_n_chips_in_graph(15)
        self.assertFalse(MachineDataView.has_n_boards_required())
        self.assertEqual(20, MachineDataView.get_n_chips_needed())

        # required higher than in graph
        writer.set_n_chips_in_graph(25)
        self.assertFalse(MachineDataView.has_n_boards_required())
        self.assertEqual(20, MachineDataView.get_n_chips_needed())

        # reset does not remove required
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        self.assertFalse(MachineDataView.has_n_boards_required())
        self.assertEqual(20, MachineDataView.get_n_chips_needed())

        writer = MachineDataWriter.setup()
        self.assertFalse(MachineDataView.has_n_boards_required())
        self.assertFalse(MachineDataView.has_n_chips_needed())

        # in graph only
        writer.set_n_chips_in_graph(25)
        self.assertEqual(25, MachineDataView.get_n_chips_needed())

        # reset clears in graph
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        self.assertFalse(MachineDataView.has_n_chips_needed())

        # N boards
        writer = MachineDataWriter.setup()
        writer.set_n_required(5, None)
        self.assertEqual(5, MachineDataView.get_n_boards_required())
        self.assertFalse(MachineDataView.has_n_chips_needed())

        # boards does not hide in graph
        writer.set_n_chips_in_graph(40)
        self.assertEqual(5, MachineDataView.get_n_boards_required())
        self.assertEqual(40, MachineDataView.get_n_chips_needed())

        # reset does not clear required
        writer.start_run()
        writer.finish_run()
        writer.hard_reset()
        self.assertEqual(5, MachineDataView.get_n_boards_required())
        self.assertFalse(MachineDataView.has_n_chips_needed())

        # two Nones fine
        writer = MachineDataWriter.setup()
        writer.set_n_required(None, None)
        self.assertFalse(MachineDataView.has_n_boards_required())
        self.assertFalse(MachineDataView.has_n_chips_needed())

        # Ilegal calls
        with self.assertRaises(ValueError):
            writer.set_n_required(5, 5)
        with self.assertRaises(ValueError):
            writer.set_n_required(None, -5)
        with self.assertRaises(ValueError):
            writer.set_n_required(0, None)
        with self.assertRaises(TypeError):
            writer.set_n_required(None, "five")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            writer.set_n_required("2.3", None)  # type: ignore[arg-type]
