"""
Testingreverseiptag
"""
from __future__ import absolute_import
# general imports
import unittest
from spinn_machine.tags import ReverseIPTag


class TestingReverseIptag(unittest.TestCase):
    """
    TestingIptag
    """

    def test_create_valid_reverse_iptag(self):
        """
        test which tests if a iptag with valid inputs works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)

    def test_retrival_of_board_address(self):
        """
        test if the board address retrival works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        board_address = reverse_ip_tag.board_address
        self.assertEqual("", board_address)

    def test_retrival_of_tag(self):
        """
        test if the board address retrival works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        tag = reverse_ip_tag.tag
        self.assertEqual(0, tag)

    def test_retrival_of_port(self):
        """
        test if the board address retrival works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        port = reverse_ip_tag.port
        self.assertEqual(port, 1)

    def test_retrival_of_dest_x(self):
        """
        test if the board address retrival works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        destination_x = reverse_ip_tag.destination_x
        self.assertEqual(destination_x, 0)

    def test_retrival_of_dest_y(self):
        """
        test if the board address retrival works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        destination_y = reverse_ip_tag.destination_y
        self.assertEqual(destination_y, 0)

    def test_retrival_of_dest_p(self):
        """
        test if the board address retrival works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        destination_p = reverse_ip_tag.destination_p
        self.assertEqual(destination_p, 1)

    def test_retrival_of_sdp_port(self):
        """
        test if the board address retrival works

        :rtype: None
        """
        reverse_ip_tag = ReverseIPTag("", 0, 1, 0, 0, 1)
        self.assertIsNotNone(reverse_ip_tag)
        sdp_port = reverse_ip_tag.sdp_port
        self.assertEqual(sdp_port, 1)


if __name__ == '__main__':
    unittest.main()
