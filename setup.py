try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNMachine",
    version="3.0.0",
    description="Representation of a SpiNNaker Machine",
    url="https://github.com/SpiNNakerManchester/SpiNNMachine",
    license="GNU GPLv3.0",
    packages=['spinn_machine',
              'spinn_machine.link_data_objects',
              'spinn_machine.tags',
              'spinn_machine.utilities']
)
