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

import spinn_utilities
import spinn_machine
from spinn_machine.config_setup import unittest_setup


def test_compare_versions():
    unittest_setup()
    spinn_utilities_parts = spinn_utilities.__version__.split('.')
    spinn_machine_parts = spinn_machine.__version__.split('.')

    assert (spinn_utilities_parts[0] == spinn_machine_parts[0])
    assert (spinn_utilities_parts[1] <= spinn_machine_parts[1])


if __name__ == '__main__':
    test_compare_versions()
