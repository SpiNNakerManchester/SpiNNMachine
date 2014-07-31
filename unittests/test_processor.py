import unittest
import spinn_machine.processor as proc


class TestingProcessor(unittest.TestCase):
    def test_creating_processors(self):
        # self.assertEqual(True, False)
        processors = list()
        flops = 1000
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        for _id in range(18):
            self.assertEqual(processors[_id].processor_id, _id)
            self.assertEqual(processors[_id].clock_speed, flops)
            self.assertFalse(processors[_id].is_monitor)

    def test_creating_monitor_processors(self):
        processors = list()
        flops = 1000
        for i in range(18):
            processors.append(proc.Processor(i, flops, is_monitor=True))

        for _id in range(18):
            self.assertEqual(processors[_id].processor_id, _id)
            self.assertEqual(processors[_id].clock_speed, flops)
            self.assertTrue(processors[_id].is_monitor)

    def test_creating_processors_with_negative_clock_speed(self):
        with self.assertRaises(Exception):
            proc.Processor(processor_id=1, clock_speed=- 5)


if __name__ == '__main__':
    unittest.main()
