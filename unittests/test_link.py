import unittest
from spinn_machine import Link


class TestingLinks(unittest.TestCase):
    def test_create_new_link(self):
        links = list()
        (e, ne, n, w, sw, s) = range(6)
        links.append(Link(0, 0, 0, 0, 1, s, s))
        self.assertEqual(links[0].source_x, 0)
        self.assertEqual(links[0].source_y, 0)
        self.assertEqual(links[0].source_link_id, 0)
        self.assertEqual(links[0].destination_x, 0)
        self.assertEqual(links[0].destination_y, 1)
        self.assertEqual(links[0].multicast_default_from, s)
        self.assertEqual(links[0].multicast_default_to, s)


if __name__ == '__main__':
    unittest.main()
