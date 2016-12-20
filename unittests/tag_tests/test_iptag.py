"""
TestingIptag
"""

# general imports
import unittest
from spinn_machine.tags.iptag import IPTag


class TestingIptag(unittest.TestCase):
    """
    TestingIptag
    """

    def test_create_valid_iptag(self):
        """
        test which tests if a iptag with valid inputs works
        :return:
        """
        IPTag("", 0, 0, 0, "", 1)

    def test_retrival_of_board_address(self):
        """
        test if the board address retrieval works
        :return:
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        board_address = iptag.board_address
        self.assertEqual("", board_address)

    def test_retrival_of_ip_address(self):
        """
        test if the board address retrieval works
        :return:
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        ip_address = iptag.ip_address
        self.assertEqual("", ip_address)

    def test_retrival_of_tag(self):
        """
        test if the board address retrieval works
        :return:
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        tag = iptag.tag
        self.assertEqual(tag, 0)

    def test_retrival_of_port(self):
        """
        test if the board address retrieval works
        :return:
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        port = iptag.port
        self.assertEqual(port, 1)

    def test_retrival_of_strip_sdp(self):
        """
        test if the board address retrieval works
        :return:
        """
        iptag = IPTag("", 0, 0, 0, "", 1)
        strip_sdp = iptag.strip_sdp
        self.assertEqual(strip_sdp, False)

if __name__ == '__main__':
    unittest.main()
