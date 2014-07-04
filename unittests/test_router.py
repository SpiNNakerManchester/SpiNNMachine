__author__ = 'Petrut'

import unittest
import spinn_machine.router as router
import spinn_machine.link as link
import spinn_machine.exceptions as exc

class TestingRouter(unittest.TestCase):
    def test_creating_new_router(self):
        links = list()
        (E, NE, N, W, SW, S) = range(6)
        links.append(link.Link(0,0,0,1,1,N,N))
        links.append(link.Link(0,1,1,1,0,S,S))
        links.append(link.Link(1,1,2,0,0,E,E))
        links.append(link.Link(1,0,3,0,1,W,W))
        r = router.Router(links)

        for i in range(4):
            self.assertTrue(r.is_link(i))
            self.assertEqual(r.get_link(i),links[i])

        self.assertFalse(r.is_link(-1))
        self.assertFalse(r.is_link(links.__len__()+1))
        self.assertEqual(r.get_link(-1),None)
        self.assertEqual(r.get_link(links.__len__()+1),None)

    def test_creating_new_router_with_duplicate_links(self):
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            links = list()
            (E, NE, N, W, SW, S) = range(6)
            links.append(link.Link(0,0,0,0,1,S,S))
            links.append(link.Link(0,1,0,0,1,S,S))
            r = router.Router(links)

if __name__ == '__main__':
    unittest.main()
