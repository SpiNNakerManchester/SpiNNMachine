""" An abstraction of a SpiNNaker Machine.  The main functionality is\
provided by :py:class:`spinn_machine.Machine`.

Functional Requirements
=======================

    * Create a machine which represents the current state of a machine, in\
      terms of the available chips, cores on the chips, SDRAM available,\
      routable links between chips and available routing entries.

    * Create a machine which represents an abstract ideal machine.

        * There can only be one chip in the machine with given x, y coordinates

        * There can only be one processor in each chip with a given processor\
          ID

        * There can only be one link in the router of each chip with a given ID

    * Add a chip to a given machine to represent an external device.

        * A chip with the same x, y coordinates must not already exist in the\
          machine

    * Add a link to a router of a given chip to represent a connection to an\
      external device.

        * A link with the given ID must not already exist in the chip

    * Create a representation of a multicast routing entry to be shared\
      between modules that deal with routing entries.

Use Cases
=========

    * :py:class:`~spinn_machine.Machine` is returned as a representation of\
      the current state of a machine.

    * :py:class:`~spinn_machine.VirtualMachine` is used as an outline of a\
      machine on which a simulation will be run, e.g., for placement of\
      executables and/or finding routes between placed executables.

    * :py:class:`~spinn_machine.Machine` is extended to add a virtual\
      :py:class:`~spinn_machine.Chip` on the machine representing an\
      external peripheral connected to the machine directly via a link from a\
      chip, so that routes can be directed to and from the external\
      peripheral.

    * :py:class:`~spinn_machine.MulticastRoutingEntry`\
      is returned in a list of entries, which indicate the current set of\
      routing entries within a multicast routing table on a chip on the\
      machine.

    * :py:class:`~spinn_machine.MulticastRoutingEntry`\
      is sent in a list of routing entries to set up routing on a chip on the\
      machine.
"""

from spinn_machine._version import __version__  # NOQA
from spinn_machine._version import __version_name__  # NOQA
from spinn_machine._version import __version_month__  # NOQA
from spinn_machine._version import __version_year__  # NOQA

from .chip import Chip
from .core_subset import CoreSubset
from .core_subsets import CoreSubsets
from .json_machine import JsonMachine
from .link import Link
from .machine import Machine
from .multicast_routing_entry import MulticastRoutingEntry
from .processor import Processor
from .router import Router
from .sdram import SDRAM
from .spinnaker_triad_geometry import SpiNNakerTriadGeometry
from .virtual_machine import VirtualMachine
from .fixed_route_entry import FixedRouteEntry


__all__ = ["Chip", "CoreSubset", "CoreSubsets", "FixedRouteEntry",
           "JsonMachine", "Link", "Machine", "MulticastRoutingEntry",
           "Processor", "Router", "SDRAM", "SpiNNakerTriadGeometry",
           "VirtualMachine"]
