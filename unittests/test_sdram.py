# Copyright (c) 2017-2019 The University of Manchester
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
