import unittest
from spinn_machine import Link


class TestingLinks(unittest.TestCase):
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
