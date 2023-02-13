# Copyright (c) 2017-2023 The University of Manchester
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
from spinn_machine import Link
from spinn_machine.config_setup import unittest_setup


class TestingLinks(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_create_new_link(self):
        links = list()
        links.append(Link(0, 0, 0, 0, 1))
        self.assertEqual(links[0].source_x, 0)
        self.assertEqual(links[0].source_y, 0)
        self.assertEqual(links[0].source_link_id, 0)
        self.assertEqual(links[0].destination_x, 0)
        self.assertEqual(links[0].destination_y, 1)


if __name__ == '__main__':
    unittest.main()
