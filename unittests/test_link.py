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
