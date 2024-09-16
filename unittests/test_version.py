# Copyright (c) 2017 The University of Manchester
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
