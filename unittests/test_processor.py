import unittest
from spinn_machine import Processor


class TestingProcessor(unittest.TestCase):
    def test_creating_processors(self):
        processors = list()
        flops = 1000
        for i in range(18):
            processors.append(Processor(i, flops))

        for _id in range(18):
            self.assertEquals(processors[_id].processor_id, _id)
            self.assertEquals(processors[_id].clock_speed, flops)
            self.assertFalse(processors[_id].is_monitor)

    def test_creating_monitor_processors(self):
        processors = list()
        flops = 1000
        for i in range(18):
            processors.append(Processor(i, flops, is_monitor=True))

        for _id in range(18):
            self.assertEquals(processors[_id].processor_id, _id)
            self.assertEquals(processors[_id].clock_speed, flops)
            self.assertTrue(processors[_id].is_monitor)

    def test_creating_processors_with_negative_clock_speed(self):
        with self.assertRaises(Exception):
            Processor(processor_id=1, clock_speed=-5)


if __name__ == '__main__':
    unittest.main()
