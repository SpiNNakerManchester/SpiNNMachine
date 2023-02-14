# Copyright (c) 2015 The University of Manchester
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

"""
TestingReverseIptag
"""
import unittest
from spinn_machine.tags import ReverseIPTag
from spinn_machine.config_setup import unittest_setup


class TestingReverseIptag(unittest.TestCase):
    """ Tests of ReverseIPTag
    """

    def setUp(self):
        unittest_setup()

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
