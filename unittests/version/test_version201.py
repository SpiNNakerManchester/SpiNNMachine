# Copyright (c) 2015 The University of Manchester
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
from spinn_machine.no_wrap_machine import NoWrapMachine
from spinn_machine.version.version_201 import Version201
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineException


class TestVersion201(unittest.TestCase):
    """ Tests of IPTag
    """
    def setUp(self):
        unittest_setup()

    def test_attributes(self):
        version = Version201()
        self.assertEqual(152, version.max_cores_per_chip)
        self.assertEqual(2**30, version.max_sdram_per_chip)
        self.assertEqual(1, version.n_scamp_cores)
        self.assertEqual("Spin2 1 Chip", version.name)
        self.assertEqual(201, version.number)
        self.assertEqual((1, 1), version.board_shape)
        self.assertEqual(1, version.n_chips_per_board)
        self.assertEqual(16384, version.n_router_entries)

    def test_verify_config_width_height(self):
        set_config("Machine", "width", "None")
        set_config("Machine", "height", "None")
        Version201()

        set_config("Machine", "width", 1)
        with self.assertRaises(SpinnMachineException):
            Version201()

        set_config("Machine", "height", 1)
        Version201()

        set_config("Machine", "width", "None")
        with self.assertRaises(SpinnMachineException):
            Version201()

    def test_set_max_lower(self):
        set_config("Machine", "max_sdram_allowed_per_chip", 1000)
        set_config("Machine", "max_machine_core", 100)
        version = Version201()
        self.assertEqual(100, version.max_cores_per_chip)
        self.assertEqual(1000, version.max_sdram_per_chip)

    def test_expected_xys(self):
        version = Version201()
        xys = version.expected_xys
        self.assertEqual(1, len(xys))
        self.assertEqual(1, len(set(xys)))
        for (x, y) in xys:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLess(x, 1)
            self.assertLess(y, 1)

    def test_expected_chip_core_map(self):
        version = Version201()
        chip_core_map = version.chip_core_map
        self.assertEqual(1, len(chip_core_map))
        for (x, y) in chip_core_map:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLess(x, 1)
            self.assertLess(y, 1)
            cores = chip_core_map[(x, y)]
            self.assertGreaterEqual(cores, 100)
            self.assertLessEqual(cores, 152)

    def test_get_potential_ethernet_chips(self):
        version = Version201()
        eths = version.get_potential_ethernet_chips(0, 0)
        self.assertListEqual([(0, 0)], eths)

        # if size is wromg GIGO
        eths = version.get_potential_ethernet_chips(8, 8)
        self.assertListEqual([(0, 0)], eths)
        eths = version.get_potential_ethernet_chips(12, 12)
        self.assertListEqual([(0, 0)], eths)
        eths = version.get_potential_ethernet_chips(16, 16)
        self.assertListEqual([(0, 0)], eths)

    def test_verify_size(self):
        version = Version201()

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
        version.verify_size(1, 1)
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

    def test_create_machine(self):
        version = Version201()

        machine = version.create_machine(width=1, height=1)
        self.assertIsInstance(machine, NoWrapMachine)

    def test_processor_info(self):
        version = Version201()
        self.assertEqual([150, 300], version.clock_speeds_hz)
        #self.assertEqual(65536, version.dtcm_bytes)


if __name__ == '__main__':
    unittest.main()
