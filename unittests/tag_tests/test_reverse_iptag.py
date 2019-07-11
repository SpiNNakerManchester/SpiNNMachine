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

"""
TestingReverseIptag
"""
from __future__ import absolute_import
import unittest
from spinn_machine.tags import ReverseIPTag


class TestingReverseIptag(unittest.TestCase):
    """ Tests of ReverseIPTag
    """

    def test_create_valid_reverse_iptag(self):
        """ test if a reverse IP tag with valid inputs works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)

    def test_retrival_of_board_address(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        board_address = reverse_ip_tag.board_address
        self.assertEqual("", board_address)

    def test_retrival_of_tag(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        tag = reverse_ip_tag.tag
        self.assertEqual(0, tag)

    def test_retrival_of_port(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        port = reverse_ip_tag.port
        self.assertEqual(port, 1)

    def test_retrival_of_dest_x(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        destination_x = reverse_ip_tag.destination_x
        self.assertEqual(destination_x, 0)

    def test_retrival_of_dest_y(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        destination_y = reverse_ip_tag.destination_y
        self.assertEqual(destination_y, 0)

    def test_retrival_of_dest_p(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        destination_p = reverse_ip_tag.destination_p
        self.assertEqual(destination_p, 1)

    def test_retrival_of_sdp_port(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        sdp_port = reverse_ip_tag.sdp_port
        self.assertEqual(sdp_port, 1)

    def test_tag_rendering(self):
        riptag = ReverseIPTag("somewhere.local", 2, 3, 4, 5, 6)
        assert riptag.__repr__() == (
            "ReverseIPTag(board_address=somewhere.local, tag=2, port=3, "
            "destination_x=4, destination_y=5, destination_p=6, sdp_port=1)")


if __name__ == '__main__':
    unittest.main()
