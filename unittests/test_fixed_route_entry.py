import unittest
from spinn_machine import FixedRouteEntry
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException


class TestingFixedRouteEntries(unittest.TestCase):
    def test_fixed_route_creation(self):
        fre = FixedRouteEntry([1, 2, 3], [2, 3, 4])
        self.assertEquals(fre.__repr__(), "{2, 3, 4}:{1, 2, 3}")
        self.assertEquals(frozenset(fre.processor_ids), frozenset([1, 2, 3]))
        self.assertEquals(frozenset(fre.link_ids), frozenset([2, 3, 4]))

    def test_fixed_route_errors(self):
        with self.assertRaises(SpinnMachineAlreadyExistsException) as e:
            FixedRouteEntry([1, 2, 2], [2, 3, 4])
        self.assertEquals(e.exception.item, "processor ID")
        self.assertEquals(e.exception.value, "2")
        with self.assertRaises(SpinnMachineAlreadyExistsException) as e:
            FixedRouteEntry([1, 2, 3], [2, 3, 2])
        self.assertEquals(e.exception.item, "link ID")
        self.assertEquals(e.exception.value, "2")


if __name__ == '__main__':
    unittest.main()
