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
TestingIptag
"""
import unittest
from spinn_machine.tags import IPTag
from spinn_machine.config_setup import unittest_setup


class TestingIptag(unittest.TestCase):
    """ Tests of IPTag
    """
    def setUp(self):
        unittest_setup()

    def test_create_valid_iptag(self):
        """ test if an IP tag with valid inputs works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)

    def test_retrival_of_board_address(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        board_address = iptag.board_address
        self.assertEqual("", board_address)

    def test_retrival_of_ip_address(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        ip_address = iptag.ip_address
        self.assertEqual("", ip_address)

    def test_retrival_of_tag(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        tag = iptag.tag
        self.assertEqual(tag, 0)

    def test_retrival_of_port(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        port = iptag.port
        self.assertEqual(port, 1)

    def test_retrival_of_strip_sdp(self):
        """ test if the board address retrieval works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        strip_sdp = iptag.strip_sdp
        self.assertEqual(strip_sdp, False)

    def test_tag_rendering(self):
        iptag = IPTag("localhost", 1, 2, 3, "abc", 4, True)
        assert iptag.__repr__() == (
            "IPTag(board_address=localhost, destination_x=1, destination_y=2, "
            "tag=3, port=4, ip_address=abc, strip_sdp=True, "
            "traffic_identifier=DEFAULT)")

    def test_in_dict(self):
        d = dict()
        iptag_1 = IPTag("", 0, 0, 0, "", 1)
        d[iptag_1] = 1
        iptag_2 = IPTag("", 0, 0, 0, "", 1, traffic_identifier="FOO")
        d[iptag_2] = 10
        d[IPTag("", 0, 0, 0, "", 1)] += 3
        assert d[iptag_1] == 4
        assert d[iptag_2] == 10
        assert len(d) == 2

    def test_set_port(self):
        tag = IPTag("examplehost", 0, 0, 0, "")
        tag.port = 1
        with self.assertRaises(RuntimeError) as e:
            tag.port = 2
        self.assertIn("Port cannot be set more than once", str(e.exception))

    def test_no_equals(self):
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertNotEqual(iptag, "foo")


if __name__ == '__main__':
    unittest.main()
