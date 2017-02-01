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

    sudo python setup.py develop

To install as a development version for only yourself, run:

    python setup.py develop --user

To install as a development version in a virtualenv, with the virutalenv
enabled, run:

    python setup.py develop