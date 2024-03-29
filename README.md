[![PyPi version](https://img.shields.io/pypi/v/SpiNNMachine.svg?style=flat)](https://pypi.org/project/SpiNNMachine/)
[![Build Status](https://github.com/SpiNNakerManchester/SpiNNMachine/workflows/Python%20Actions/badge.svg?branch=master)](https://github.com/SpiNNakerManchester/SpiNNMachine/actions?query=workflow%3A%22Python+Actions%22+branch%3Amaster)
[![Documentation Status](https://readthedocs.org/projects/spinnmachine/badge/?version=latest)](https://spinnmachine.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/SpiNNakerManchester/SpiNNMachine/badge.svg?branch=master)](https://coveralls.io/github/SpiNNakerManchester/SpiNNMachine?branch=master)

This package is part of the [SpiNNaker Project](http://apt.cs.manchester.ac.uk/projects/SpiNNaker/) .

This package is used to provide a Python representation of a SpiNNaker machine

User Installation
=================
If you want to install for all users, run:

    sudo pip install SpiNNMachine

If you want to install only for yourself, run:

    pip install SpiNNMachine --user

To install in a virtualenv, with the virtualenv enabled, run:

    pip install SpiNNMachine

Developer Installation
======================
If you want to be able to edit the source code, but still have it referenced
from other Python modules, you can set the install to be a developer install.
In this case, download the source code, and extract it locally, or else clone
the git repository:

    git clone http://github.com/SpiNNakerManchester/SpiNNMachine.git

To install as a development version which all users will then be able to use,
run the following where the code has been extracted:

    sudo pip install -e .

To install as a development version for only yourself, run:

    pip install -e . --user

To install as a development version in a `virtualenv`, with the `virutalenv`
enabled, run:

    pip install -e .

Test Installation
=================
To be able to run the unitests add [Test] to the pip installs above

    pip install -e .[Test]

Documentation
=============
[SpiNNMachine python documentation](http://spinnmachine.readthedocs.io)

[Combined python documentation](http://spinnakermanchester.readthedocs.io)
