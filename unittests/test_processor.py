__author__ = 'Petrut'

import unittest
import spinn_machine.processor as proc

class TestingProcessor(unittest.TestCase):
    def test_creating_processors(self):
        #self.assertEqual(True, False)
        processors = list()
        flops = 1000
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        for id in range(18):
            self.assertEqual(processors[id].processor_id, id)
            self.assertEqual(processors[id].clock_speed, flops)
            self.assertFalse(processors[id].is_monitor)

    def test_creating_monitor_processors(self):
        processors = list()
        flops = 1000
        for i in range(18):
            processors.append(proc.Processor(i, flops,is_monitor = True))

        for id in range(18):
            self.assertEqual(processors[id].processor_id, id)
            self.assertEqual(processors[id].clock_speed, flops)
            self.assertTrue(processors[id].is_monitor)

    def test_creating_processors_with_negative_clock_speed(self):
        with self.assertRaises(Exception):
            proc.Processor(processor_id= 1, clock_speed= - 5)


if __name__ == '__main__':
    unittest.main()
