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
from spinn_machine.version.version_5 import Version5
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineException


class TestVersion5(unittest.TestCase):
    """ Tests of IPTag
    """
    def setUp(self):
        unittest_setup()

    def test_attributes(self):
        version = Version5()
        self.assertEqual(18, version.max_cores_per_chip)
        self.assertEqual(123469792, version.max_sdram_per_chip)
        self.assertEqual(1, version.n_non_user_cores)
        self.assertEqual("Spin1 48 Chip", version.name)
        self.assertEqual(48, version.n_chips_per_board)
        self.assertEqual(1023, version.n_router_entrie)

    def test_verify_config_width_height(self):
        set_config("Machine", "width", "None")
        set_config("Machine", "height", "None")
        Version5()

        set_config("Machine", "width", 8)
        with self.assertRaises(SpinnMachineException):
            Version5()

        set_config("Machine", "height", 8)
        Version5()

        set_config("Machine", "width", "None")
        with self.assertRaises(SpinnMachineException):
            Version5()

    def test_set_max_lower(self):
        set_config("Machine", "max_sdram_allowed_per_chip", 1000)
        set_config("Machine", "max_machine_core", 10)
        version = Version5()
        self.assertEqual(10, version.max_cores_per_chip)
        self.assertEqual(1000, version.max_sdram_per_chip)

    def test_expected_xys(self):
        version = Version5()
        xys = version.expected_xys
        self.assertEqual(48, len(xys))
        self.assertEqual(48, len(set(xys)))
        for (x, y) in xys:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLess(x, 8)
            self.assertLess(y, 8)


if __name__ == '__main__':
    unittest.main()
