"""
runs all spinn machine tests scripts
"""
import unittest

testmodules = ['test_chip', 'test_link', 'test_machine',
               'test_multicast_routing_entry', 'test_processor', 'test_router',
               'test_sdram', 'test_virtual_machine', 'tag_tests.test_iptag',
               'tag_tests.test_reverse_iptag']

suite = unittest.TestSuite()

for t in testmodules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

unittest.TextTestRunner().run(suite)