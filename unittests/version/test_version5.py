# Copyright (c) 2023 The University of Manchester
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
Testing Version5
"""
import unittest
from spinn_utilities.config_holder import set_config
from spinn_machine.full_wrap_machine import FullWrapMachine
from spinn_machine.no_wrap_machine import NoWrapMachine
from spinn_machine.horizontal_wrap_machine import HorizontalWrapMachine
from spinn_machine.vertical_wrap_machine import VerticalWrapMachine
from spinn_machine.version.version_5 import Version5
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineException


class TestVersion5(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_attributes(self) -> None:
        version = Version5()
        self.assertEqual(18, version.max_cores_per_chip)
        self.assertEqual(123469792, version.max_sdram_per_chip)
        self.assertEqual(1, version.n_scamp_cores)
        self.assertEqual("Spin1 48 Chip", version.name)
        self.assertEqual(5, version.number)
        self.assertEqual((8, 8), version.board_shape)
        self.assertEqual(48, version.n_chips_per_board)
        self.assertEqual(1023, version.n_router_entries)

    def test_verify_config_width_height(self) -> None:
        set_config("Machine", "width", "None")
        set_config("Machine", "height", "None")
        Version5()

        set_config("Machine", "width", "8")
        with self.assertRaises(SpinnMachineException):
            Version5()

        set_config("Machine", "height", "8")
        Version5()

        set_config("Machine", "width", "None")
        with self.assertRaises(SpinnMachineException):
            Version5()

    def test_set_max_lower(self) -> None:
        set_config("Machine", "max_sdram_allowed_per_chip", "1000")
        set_config("Machine", "max_machine_core", "10")
        version = Version5()
        self.assertEqual(10, version.max_cores_per_chip)
        self.assertEqual(1000, version.max_sdram_per_chip)

    def test_expected_xys(self) -> None:
        version = Version5()
        xys = version.expected_xys
        self.assertEqual(48, len(xys))
        self.assertEqual(48, len(set(xys)))
        for (x, y) in xys:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLess(x, 8)
            self.assertLess(y, 8)

    def test_expected_chip_core_map(self) -> None:
        version = Version5()
        chip_core_map = version.chip_core_map
        self.assertEqual(48, len(chip_core_map))
        for (x, y) in chip_core_map:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLess(x, 8)
            self.assertLess(y, 8)
            cores = chip_core_map[(x, y)]
            self.assertGreaterEqual(cores, 16)
            self.assertLessEqual(cores, 18)

    def test_get_potential_ethernet_chips(self) -> None:
        version = Version5()
        eths = version.get_potential_ethernet_chips(8, 8)
        self.assertSequenceEqual([(0, 0)], eths)
        eths = version.get_potential_ethernet_chips(12, 12)
        self.assertSequenceEqual([(0, 0), (4, 8), (8, 4)], eths)
        eths = version.get_potential_ethernet_chips(16, 16)
        self.assertSequenceEqual([(0, 0), (4, 8), (8, 4)], eths)

        # if size is wrong GIGO
        eths = version.get_potential_ethernet_chips(2, 2)
        self.assertSequenceEqual([(0, 0)], eths)

    def test_verify_size(self) -> None:
        version = Version5()

        with self.assertRaises(SpinnMachineException):
            version.verify_size(12, -12)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(-12, 12)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(12, None)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(None, 12)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(12, 8)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(8, 12)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(2, 2)

        version.verify_size(8, 8)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(12, 8)
        version.verify_size(12, 12)
        version.verify_size(12, 16)
        version.verify_size(16, 12)
        version.verify_size(16, 16)

    def test_create_machin(self) -> None:
        version = Version5()

        machine = version.create_machine(width=8, height=8)
        self.assertIsInstance(machine,  NoWrapMachine)

        machine = version.create_machine(16, 16)
        self.assertIsInstance(machine,  NoWrapMachine)

        machine = version.create_machine(12, 16)
        self.assertIsInstance(machine, HorizontalWrapMachine)
        machine = version.create_machine(16, 12)
        self.assertIsInstance(machine, VerticalWrapMachine)
        machine = version.create_machine(12, 12)
        self.assertIsInstance(machine, FullWrapMachine)

    def test_processor_info(self) -> None:
        version = Version5()
        self.assertEqual([200], version.clock_speeds_hz)
        self.assertEqual(65536, version.dtcm_bytes)

    def test_size_from_n_cores(self) -> None:
        version = Version5()
        self.assertEqual((8, 8), version.size_from_n_cores(10))
        # standard for there to be 8 17 core Chips and each has 1 scamp core
        n_cores = 17 * 48 - 8
        self.assertEqual((8, 8), version.size_from_n_cores(n_cores))
        self.assertEqual((16, 16), version.size_from_n_cores(n_cores + 1))
        self.assertEqual((16, 16), version.size_from_n_cores(n_cores * 3))
        self.assertEqual((28, 16), version.size_from_n_cores(n_cores * 4))
        self.assertEqual((28, 16), version.size_from_n_cores(n_cores * 6))
        self.assertEqual((28, 28), version.size_from_n_cores(n_cores * 7))
        self.assertEqual((28, 28), version.size_from_n_cores(n_cores * 12))
        self.assertEqual((40, 28), version.size_from_n_cores(n_cores * 13))
        self.assertEqual((40, 28), version.size_from_n_cores(n_cores * 18))
        self.assertEqual((40, 40), version.size_from_n_cores(n_cores * 18 + 1))

    def test_size_from_n_chips(self) -> None:
        version = Version5()
        self.assertEqual((8, 8), version.size_from_n_chips(1))
        self.assertEqual((8, 8), version.size_from_n_chips(48))
        self.assertEqual((16, 16), version.size_from_n_chips(49))


if __name__ == '__main__':
    unittest.main()
