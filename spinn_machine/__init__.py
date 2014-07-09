""" A python abstraction of a SpiNNaker Machine.  The main functionality\
    is provided by :py:class:`spinn_machine.machine.Machine`.
    
    Functional Requirements
    =======================
    
        * Create a machine which represents the current state of a machine, in\
          terms of the available chips, cores on the chips, SDRAM available,
          routable links between chips and available routing entries.
          
        * Create a machine which represents an abstract ideal machine.
        
            * There can only be one chip in the machine with given x, y\
              coordinates
              
            * There can only be one processor in each chip with a given\
              processor id
            
            * There can only be one link in the router of each chip with\
              a given id
        
        * Add a chip to a given machine to represent an external device.
        
            * A chip with the same x, y coordinates must not already exist\
              in the machine
        
        * Add a link to a router of a given chip to represent a connection\
          to an external device.
          
            * A link with the given id must not already exist in the chip
          
        * Create a representation of a multicast routing entry to be shared\
          between modules that deal with routing entries.
    
    Use Cases
    =========
    
        * :py:class:`~spinn_machine.machine.Machine` is returned as a\
          representation of the current state of a machine.
          
        * :py:class:`~spinn_machine.machine.Machine` is used as an outline of\
          a machine on which a simulation will be run e.g. for placement of\
          executables and/or finding routes between placed executables.
          
        * :py:class:`~spinn_machine.machine.Machine` is extended to add\
          a virtual :py:class:`~spinn_machine.chip.Chip` on the machine\
          representing an external peripheral connected to the machine directly\
          via a link from a chip, so that routes can be directed to and from\
          the external peripheral
          
        * :py:class:`~spinn_machine.multicast_routing_entry.MulticastRoutingEntry`\
          is returned in a list of entries, which indicate the current set\
          of routing entries within a multicast routing table on a chip on the\
          machine.
          
        * :py:class:`~spinn_machine.multicast_routing_entry.MulticastRoutingEntry`\
          is sent in a list of routing entries to set up routing on a chip\
          on the machine.
"""