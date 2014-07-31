import unittest
import spinn_machine.router as router
import spinn_machine.link as link
import spinn_machine.exceptions as exc


class TestingRouter(unittest.TestCase):
    def test_creating_new_router(self):
        links = list()
        (e, ne, n, w, sw, s) = range(6)
        links.append(link.Link(0, 0, 0, 1, 1, n, n))
        links.append(link.Link(0, 1, 1, 1, 0, s, s))
        links.append(link.Link(1, 1, 2, 0, 0, e, e))
        links.append(link.Link(1, 0, 3, 0, 1, w, w))
        r = router.Router(links, False, 100, 1024)

        for i in range(4):
            self.assertTrue(r.is_link(i))
            self.assertEqual(r.get_link(i), links[i])

        self.assertFalse(r.emergency_routing_enabled)
        self.assertEqual(r.clock_speed, 100)
        self.assertEqual(r.n_available_multicast_entries, 1024)

        self.assertFalse(r.is_link(-1))
        self.assertFalse(r.is_link(links.__len__() + 1))
        self.assertEqual(r.get_link(-1), None)
        self.assertEqual(r.get_link(links.__len__() + 1), None)

    def test_creating_new_router_with_emergency_routing_on(self):
        links = list()
        (e, ne, n, w, sw, s) = range(6)
        links.append(link.Link(0, 0, 0, 0, 1, s, s))
        links.append(link.Link(0, 1, 1, 0, 1, s, s))
        r = router.Router(links, True, 100, 1024)
        self.assertTrue(r.emergency_routing_enabled)

    def test_creating_new_router_with_duplicate_links(self):
        with self.assertRaises(exc.SpinnMachineAlreadyExistsException):
            links = list()
            (e, ne, n, w, sw, s) = range(6)
            links.append(link.Link(0, 0, 0, 0, 1, s, s))
            links.append(link.Link(0, 1, 0, 0, 1, s, s))
            router.Router(links, False, 100, 1024)


if __name__ == '__main__':
    unittest.main()
