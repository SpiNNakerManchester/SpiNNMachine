__author__ = 'Petrut'

import unittest
import spinn_machine.processor as proc

class TestingProcessor(unittest.TestCase):
    def test_creating_processors(self):
        #self.assertEqual(True, False)
        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i))

        for id in range(18):
            self.assertEqual(processors[id]._processor_id, id)



if __name__ == '__main__':
    unittest.main()
