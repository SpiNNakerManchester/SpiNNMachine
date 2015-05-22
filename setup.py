try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNMachine",
    version="2015.003-rc-01",
    description="Representation of a SpiNNaker Machine",
    url="https://github.com/SpiNNakerManchester/SpiNNMachine",
    license="GNU GPLv3.0",
    packages=['spinn_machine',
              'spinn_machine.tags']
)
