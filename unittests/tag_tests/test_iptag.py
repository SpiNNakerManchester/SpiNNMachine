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
TestingIptag
"""
import unittest
from spinn_machine.tags import IPTag
from spinn_machine.config_setup import unittest_setup


class TestingIptag(unittest.TestCase):
    """ Tests of IPTag
    """
    def setUp(self) -> None:
        unittest_setup()

    def test_create_valid_iptag(self) -> None:
        """ test if an IP tag with valid inputs works
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)

    def test_retrival_of_board_address(self) -> None:
        """ test if the board address retrieval works
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        board_address = iptag.board_address
        self.assertEqual("", board_address)

    def test_retrival_of_ip_address(self) -> None:
        """ test if the board address retrieval works
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        ip_address = iptag.ip_address
        self.assertEqual("", ip_address)

    def test_retrival_of_tag(self) -> None:
        """ test if the board address retrieval works
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        tag = iptag.tag
        self.assertEqual(tag, 0)

    def test_retrival_of_port(self) -> None:
        """ test if the board address retrieval works
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        port = iptag.port
        self.assertEqual(port, 1)

    def test_retrival_of_strip_sdp(self) -> None:
        """ test if the board address retrieval works
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        strip_sdp = iptag.strip_sdp
        self.assertEqual(strip_sdp, False)

    def test_tag_rendering(self) -> None:
        iptag = IPTag("localhost", 1, 2, 3, "abc", 4, True)
        assert iptag.__repr__() == (
            "IPTag(board_address=localhost, destination_x=1, destination_y=2, "
            "tag=3, port=4, ip_address=abc, strip_sdp=True, "
            "traffic_identifier=DEFAULT)")

    def test_in_dict(self) -> None:
        d = dict()
        iptag_1 = IPTag("", 0, 0, 0, "", 1)
        d[iptag_1] = 1
        iptag_2 = IPTag("", 0, 0, 0, "", 1, traffic_identifier="FOO")
        d[iptag_2] = 10
        d[IPTag("", 0, 0, 0, "", 1)] += 3
        assert d[iptag_1] == 4
        assert d[iptag_2] == 10
        assert len(d) == 2

    def test_no_equals(self) -> None:
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertNotEqual(iptag, "foo")


if __name__ == '__main__':
    unittest.main()
