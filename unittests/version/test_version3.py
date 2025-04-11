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
from spinn_machine.version.version_3 import Version3
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineException


class TestVersion3(unittest.TestCase):

    def setUp(self) -> None:
        unittest_setup()

    def test_attributes(self) -> None:
        version = Version3()
        self.assertEqual(18, version.max_cores_per_chip)
        self.assertEqual(123469792, version.max_sdram_per_chip)
        self.assertEqual(1, version.n_scamp_cores)
        self.assertEqual("Spin1 4 Chip", version.name)
        self.assertEqual(3, version.number)
        self.assertEqual((2, 2), version.board_shape)
        self.assertEqual(4, version.n_chips_per_board)
        self.assertEqual(1023, version.n_router_entries)

    def test_verify_config_width_height(self) -> None:
        set_config("Machine", "width", "None")
        set_config("Machine", "height", "None")
        Version3()

        set_config("Machine", "width", "2")
        with self.assertRaises(SpinnMachineException):
            Version3()

        set_config("Machine", "height", "2")
        Version3()

        set_config("Machine", "width", "None")
        with self.assertRaises(SpinnMachineException):
            Version3()

    def test_set_max_lower(self) -> None:
        set_config("Machine", "max_sdram_allowed_per_chip", "1000")
        set_config("Machine", "max_machine_core", "10")
        version = Version3()
        self.assertEqual(10, version.max_cores_per_chip)
        self.assertEqual(1000, version.max_sdram_per_chip)

    def test_expected_xys(self) -> None:
        version = Version3()
        xys = version.expected_xys
        self.assertEqual(4, len(xys))
        self.assertEqual(4, len(set(xys)))
        for (x, y) in xys:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLess(x, 2)
            self.assertLess(y, 2)

    def test_expected_chip_core_map(self) -> None:
        version = Version3()
        chip_core_map = version.chip_core_map
        self.assertEqual(4, len(chip_core_map))
        for (x, y) in chip_core_map:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLess(x, 2)
            self.assertLess(y, 2)
            cores = chip_core_map[(x, y)]
            self.assertGreaterEqual(cores, 16)
            self.assertLessEqual(cores, 18)

    def test_get_potential_ethernet_chips(self) -> None:
        version = Version3()
        eths = version.get_potential_ethernet_chips(2, 2)
        self.assertSequenceEqual([(0, 0)], eths)

        # if size is wromg GIGO
        eths = version.get_potential_ethernet_chips(8, 8)
        self.assertSequenceEqual([(0, 0)], eths)
        eths = version.get_potential_ethernet_chips(12, 12)
        self.assertSequenceEqual([(0, 0)], eths)
        eths = version.get_potential_ethernet_chips(16, 16)
        self.assertSequenceEqual([(0, 0)], eths)

    def test_verify_size(self) -> None:
        version = Version3()

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
        version.verify_size(2, 2)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(8, 8)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(12, 8)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(12, 12)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(12, 16)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(16, 12)
        with self.assertRaises(SpinnMachineException):
            version.verify_size(16, 16)

    def test_create_machin(self) -> None:
        version = Version3()

        machine = version.create_machine(width=2, height=2)
        self.assertIsInstance(machine, FullWrapMachine)

    def test_processor_info(self) -> None:
        version = Version3()
        self.assertEqual([200000000], version.clock_speeds_hz)
        self.assertEqual(65536, version.dtcm_bytes)

    def test_size_from_n_cores(self) -> None:
        version = Version3()
        self.assertEqual((2, 2), version.size_from_n_cores(10))
        self.assertEqual((2, 2), version.size_from_n_cores(17 * 4))
        with self.assertRaises(SpinnMachineException):
            version.size_from_n_cores(17 * 4 + 1)

    def test_size_from_n_chips(self) -> None:
        version = Version3()
        self.assertEqual((2, 2), version.size_from_n_chips(1))
        self.assertEqual((2, 2), version.size_from_n_chips(4))
        with self.assertRaises(SpinnMachineException):
            version.size_from_n_chips(5)


if __name__ == '__main__':
    unittest.main()
