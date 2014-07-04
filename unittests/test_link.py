__author__ = 'Petrut'

import unittest
import spinn_machine.link as link

class TestingLinks(unittest.TestCase):
    def test_create_new_link(self):
        #self.assertEqual(True, False)
        links = list()
        (E, NE, N, W, SW, S) = range(6)
        links.append(link.Link(0,0,N,0,1,S,S))
        self.assertEqual(links[0].source_x,0)
        self.assertEqual(links[0].source_y,0)

        self.assertEqual(links[0].source_link_id,N)

        self.assertEqual(links[0].destination_x,0)
        self.assertEqual(links[0].destination_y,1)

        self.assertEqual(links[0].multicast_default_from,S)
        self.assertEqual(links[0].multicast_default_to,S)



if __name__ == '__main__':
    unittest.main()
