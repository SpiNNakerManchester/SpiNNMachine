import unittest
from spinn_machine import FixedRouteEntry
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException


class TestingFixedRouteEntries(unittest.TestCase):
    def test_fixed_route_creation(self):
        fre = FixedRouteEntry([1, 2, 3], [2, 3, 4])
        self.assertEqual(fre.__repr__(), "set([2, 3, 4]):set([1, 2, 3])")
        self.assertEqual(frozenset(fre.processor_ids), frozenset([1, 2, 3]))
        self.assertEqual(frozenset(fre.link_ids), frozenset([2, 3, 4]))

    def test_fixed_route_errors(self):
        with self.assertRaises(SpinnMachineAlreadyExistsException) as e:
            FixedRouteEntry([1, 2, 2], [2, 3, 4])
        self.assertEqual(e.exception.item, "processor id")
        self.assertEqual(e.exception.value, "2")
        with self.assertRaises(SpinnMachineAlreadyExistsException) as e:
            FixedRouteEntry([1, 2, 3], [2, 3, 2])
        self.assertEqual(e.exception.item, "link id")
        self.assertEqual(e.exception.value, "2")


if __name__ == '__main__':
    unittest.main()
