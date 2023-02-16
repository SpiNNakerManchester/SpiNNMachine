# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from spinn_machine import SDRAM
from spinn_machine.config_setup import unittest_setup
from spinn_machine.exceptions import SpinnMachineInvalidParameterException


class TestingSDRAM(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_creating_new_sdram_object(self):
        ram = SDRAM(128)
        self.assertEqual(ram.size, 128)

    def test_creating_new_sdram_with_zero_size(self):
        ram = SDRAM(0)
        self.assertEqual(ram.size, 0)

    def test_creating_sdram_with_negative_size(self):
        with self.assertRaises(SpinnMachineInvalidParameterException):
            SDRAM(-64)


if __name__ == '__main__':
    unittest.main()
