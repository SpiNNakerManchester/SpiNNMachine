"""
TestingIptag
"""
from __future__ import absolute_import
import unittest
from spinn_machine.tags import IPTag


class TestingIptag(unittest.TestCase):
    """
    TestingIptag
    """

    def test_create_valid_iptag(self):
        """
        test which tests if a iptag with valid inputs works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)

    def test_retrival_of_board_address(self):
        """
        test if the board address retrieval works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        board_address = iptag.board_address
        self.assertEqual("", board_address)

    def test_retrival_of_ip_address(self):
        """
        test if the board address retrieval works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        ip_address = iptag.ip_address
        self.assertEqual("", ip_address)

    def test_retrival_of_tag(self):
        """
        test if the board address retrieval works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        tag = iptag.tag
        self.assertEqual(tag, 0)

    def test_retrival_of_port(self):
        """
        test if the board address retrieval works

        :rtype: None
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        self.assertIsNotNone(iptag)
        port = iptag.port
        self.assertEqual(port, 1)

    def test_retrival_of_strip_sdp(self):
        """
        test if the board address retrieval works

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


if __name__ == '__main__':
    unittest.main()
