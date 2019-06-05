import unittest
from spinn_machine import Router, Link, MulticastRoutingEntry
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException


class TestingRouter(unittest.TestCase):
    def test_creating_new_router(self):
        links = list()
        (e, ne, n, w, sw, s) = range(6)
        links.append(Link(0, 0, 0, 1, 1, n, n))
        links.append(Link(0, 1, 1, 1, 0, s, s))
        links.append(Link(1, 1, 2, 0, 0, e, e))
        links.append(Link(1, 0, 3, 0, 1, w, w))
        r = Router(links, False, 100, 1024)

        self.assertEquals(len(r), 4)
        for i in range(4):
            self.assertTrue(r.is_link(i))
            self.assertTrue(i in r)
            self.assertEquals(r.get_link(i), links[i])
            self.assertEquals(r[i], links[i])
        self.assertEquals([l[0] for l in r], [0, 1, 2, 3])
        self.assertEquals([l[1].source_link_id for l in r], [0, 1, 2, 3])

        self.assertFalse(r.emergency_routing_enabled)
        self.assertEquals(r.clock_speed, 100)
        self.assertEquals(r.n_available_multicast_entries, 1024)

        self.assertFalse(r.is_link(-1))
        self.assertFalse(r.is_link(links.__len__() + 1))
        self.assertEquals(r.get_link(-1), None)
        self.assertEquals(r.get_link(links.__len__() + 1), None)

        self.assertEquals(r.get_neighbouring_chips_coords(),
                         [{'x': 1, 'y': 1}, {'x': 1, 'y': 0},
                          {'x': 0, 'y': 0}, {'x': 0, 'y': 1}])
        self.assertEquals(
            r.__repr__(),
            "[Router: clock_speed=0 MHz, emergency_routing=False, "
            "available_entries=1024, links=[[Link: source_x=0, source_y=0, "
            "source_link_id=0, destination_x=1, destination_y=1, "
            "default_from=2, default_to=2], [Link: source_x=0, source_y=1, "
            "source_link_id=1, destination_x=1, destination_y=0, "
            "default_from=5, default_to=5], [Link: source_x=1, source_y=1, "
            "source_link_id=2, destination_x=0, destination_y=0, "
            "default_from=0, default_to=0], [Link: source_x=1, source_y=0, "
            "source_link_id=3, destination_x=0, destination_y=1, "
            "default_from=3, default_to=3]]]")

    def test_creating_new_router_with_emergency_routing_on(self):
        links = list()
        (e, ne, n, w, sw, s) = range(6)
        links.append(Link(0, 0, 0, 0, 1, s, s))
        links.append(Link(0, 1, 1, 0, 1, s, s))
        r = Router(links, True, 100, 1024)
        self.assertTrue(r.emergency_routing_enabled)

    def test_creating_new_router_with_duplicate_links(self):
        links = list()
        (e, ne, n, w, sw, s) = range(6)
        links.append(Link(0, 0, 0, 0, 1, s, s))
        links.append(Link(0, 1, 0, 0, 1, s, s))
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            Router(links, False, 100, 1024)

    def test_convert_to_route(self):
        e = MulticastRoutingEntry(28, 60, [4, 5, 7], [1, 3, 5], True)
        r = Router.convert_routing_table_entry_to_spinnaker_route(e)
        self.assertEquals(r, 11306)


if __name__ == '__main__':
    unittest.main()
