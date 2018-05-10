import pickle
import unittest
from spinn_machine import MulticastRoutingEntry
from spinn_machine.exceptions import (
    SpinnMachineAlreadyExistsException, SpinnMachineInvalidParameterException)


class TestMulticastRoutingEntry(unittest.TestCase):
    def test_creating_new_multicast_routing_entry(self):
        link_ids = list()
        proc_ids = list()
        for i in range(6):
            link_ids.append(i)
        for i in range(18):
            proc_ids.append(i)
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key, mask, proc_ids, link_ids, True)

        self.assertEqual(a_multicast.routing_entry_key, key)
        self.assertEqual(a_multicast.link_ids, set(link_ids))
        self.assertEqual(a_multicast.mask, mask)
        self.assertEqual(a_multicast.processor_ids, set(proc_ids))
        # While we're here, let's check a few other basic ops
        self.assertEqual(str(a_multicast),
                         "1:1:True:{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,"
                         " 12, 13, 14, 15, 16, 17}:{0, 1, 2, 3, 4, 5}")
        self.assertEqual(
            a_multicast,
            pickle.loads(pickle.dumps(a_multicast, pickle.HIGHEST_PROTOCOL)))

    def test_duplicate_processors_ids(self):
        link_ids = list()
        proc_ids = list()
        for i in range(6):
            link_ids.append(i)
        for i in range(18):
            proc_ids.append(i)
        proc_ids.append(0)
        key = 1
        mask = 1
        with self.assertRaises(SpinnMachineAlreadyExistsException) as e:
            MulticastRoutingEntry(key, mask, proc_ids, link_ids, True)
        self.assertEqual(e.exception.item, "processor id")
        self.assertEqual(e.exception.value, "0")

    def test_duplicate_link_ids(self):
        link_ids = list()
        proc_ids = list()
        for i in range(6):
            link_ids.append(i)
        link_ids.append(3)
        for i in range(18):
            proc_ids.append(i)
        key = 1
        mask = 1
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            MulticastRoutingEntry(key, mask, proc_ids, link_ids, True)

    def test_duplicate_link_ids_and_proc_ids(self):
        link_ids = list()
        proc_ids = list()
        for i in range(6):
            link_ids.append(i)
        link_ids.append(3)
        for i in range(18):
            proc_ids.append(i)
        proc_ids.append(0)
        key = 1
        mask = 1
        with self.assertRaises(SpinnMachineAlreadyExistsException):
            MulticastRoutingEntry(key, mask, proc_ids, link_ids, True)

    def test_merger(self):
        link_ids = list()
        link_ids2 = list()
        proc_ids = list()
        proc_ids2 = list()
        for i in range(3):
            link_ids.append(i)
        for i in range(3, 6):
            link_ids2.append(i)
        for i in range(9):
            proc_ids.append(i)
        for i in range(9, 18):
            proc_ids2.append(i)
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key, mask, proc_ids, link_ids, True)
        b_multicast = MulticastRoutingEntry(
            key, mask, proc_ids2, link_ids2, True)

        result_multicast = a_multicast.merge(b_multicast)
        comparison_link_ids = list()
        comparison_proc_ids = list()
        for i in range(6):
            comparison_link_ids.append(i)
        self.assertEqual(link_ids + link_ids2, comparison_link_ids)
        for i in range(18):
            comparison_proc_ids.append(i)
        self.assertEqual(proc_ids + proc_ids2, comparison_proc_ids)

        self.assertEqual(result_multicast.routing_entry_key, key)
        self.assertEqual(result_multicast.link_ids, set(comparison_link_ids))
        self.assertEqual(result_multicast.mask, mask)
        self.assertEqual(result_multicast.processor_ids,
                         set(comparison_proc_ids))

    def test_merger_with_different_defaultable(self):
        link_ids = list()
        link_ids2 = list()
        proc_ids = list()
        proc_ids2 = list()
        for i in range(3):
            link_ids.append(i)
        for i in range(3, 6):
            link_ids2.append(i)
        for i in range(9):
            proc_ids.append(i)
        for i in range(9, 18):
            proc_ids2.append(i)
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key, mask, proc_ids, link_ids, True)
        b_multicast = MulticastRoutingEntry(
            key, mask, proc_ids2, link_ids2, False)

        result_multicast = a_multicast.merge(b_multicast)
        comparison_link_ids = list()
        comparison_proc_ids = list()
        for i in range(6):
            comparison_link_ids.append(i)
        self.assertEqual(link_ids + link_ids2, comparison_link_ids)
        for i in range(18):
            comparison_proc_ids.append(i)
        self.assertEqual(proc_ids + proc_ids2, comparison_proc_ids)

        self.assertEqual(result_multicast.routing_entry_key, key)
        self.assertEqual(result_multicast.link_ids, set(comparison_link_ids))
        self.assertEqual(result_multicast.mask, mask)
        self.assertEqual(result_multicast.processor_ids,
                         set(comparison_proc_ids))
        self.assertEqual(result_multicast, a_multicast + b_multicast)
        self.assertEqual(result_multicast, a_multicast | b_multicast)
        self.assertNotEqual(result_multicast, a_multicast)
        self.assertNotEqual(result_multicast, b_multicast)

    def test_merger_with_invalid_parameter_key(self):
        link_ids = list()
        link_ids2 = list()
        proc_ids = list()
        proc_ids2 = list()
        for i in range(3):
            link_ids.append(i)
        for i in range(3, 6):
            link_ids2.append(i)
        for i in range(9):
            proc_ids.append(i)
        for i in range(9, 18):
            proc_ids2.append(i)
        key_combo = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key_combo, mask, proc_ids, link_ids, True)
        b_multicast = MulticastRoutingEntry(
            key_combo + 1, mask + 1, proc_ids2, link_ids2, True)
        with self.assertRaises(SpinnMachineInvalidParameterException) as e:
            a_multicast.merge(b_multicast)
        self.assertEqual(e.exception.parameter, "other_entry.key")
        self.assertEqual(e.exception.value, "0x2")
        self.assertEqual(e.exception.problem, "The key does not match 0x1")

    def test_merger_with_invalid_parameter_mask(self):
        link_ids = list()
        link_ids2 = list()
        proc_ids = list()
        proc_ids2 = list()
        for i in range(3):
            link_ids.append(i)
        for i in range(3, 6):
            link_ids2.append(i)
        for i in range(9):
            proc_ids.append(i)
        for i in range(9, 18):
            proc_ids2.append(i)
        key = 1
        mask = 1
        a_multicast = MulticastRoutingEntry(
            key, mask, proc_ids, link_ids, True)
        b_multicast = MulticastRoutingEntry(
            key + 1, mask + 1, proc_ids2, link_ids2, True)
        with self.assertRaises(SpinnMachineInvalidParameterException):
            a_multicast.merge(b_multicast)


if __name__ == '__main__':
    unittest.main()
