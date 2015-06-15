"""
Machine
"""

# spinnmanchine imports
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException
from spinn_machine.utilities.ordered_set import OrderedSet

#general imports
from collections import OrderedDict
from collections import deque
import math

class Machine(object):
    """ A Representation of a Machine with a number of Chips.  Machine is also\
        iterable, providing ((x, y), chip) where:
        
            * x is the x-coordinate of a chip
            * y is the y-coordinate of a chip
            * chip is the chip with the given x, y coordinates
    """

    def __init__(self, chips):
        """
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`spinn_machine.chip.Chip`
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    any two chips have the same x and y coordinates
        """
        
        # The maximum chip x coordinate
        self._max_chip_x = 0
        
        # The maximum chip y coordinate
        self._max_chip_y = 0
        
        # The list of chips with ethernet connections
        self._ethernet_connected_chips = list()
        
        # The dictionary of chips
        self._chips = OrderedDict()
        self.add_chips(chips)

    def add_chip(self, chip):
        """ Add a chip to the machine
        
        :param chip: The chip to add to the machine
        :type chip: :py:class:`spinn_machine.chip.Chip`
        :return: Nothing is returned
        :rtype: None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    a chip with the same x and y coordinates already exists
        """
        chip_id = (chip.x, chip.y)
        if chip_id in self._chips:
            raise SpinnMachineAlreadyExistsException("chip", "{}, {}"
                                                     .format(chip.x, chip.y))
        
        self._chips[chip_id] = chip
        
        if chip.x > self._max_chip_x:
            self._max_chip_x = chip.x
        if chip.y > self._max_chip_y:
            self._max_chip_y = chip.y
            
        if chip.ip_address is not None:
            self._ethernet_connected_chips.append(chip)

    def add_chips(self, chips):
        """ Add some chips to the machine
        
        :param chips: an iterable of chips
        :type chips: iterable of :py:class:`spinn_machine.chip.Chip`
        :return: Nothing is returned
        :rtype: None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    a chip with the same x and y coordinates as one being\
                    added already exists
        """
        for next_chip in chips:
            self.add_chip(next_chip)

    @property
    def chips(self):
        """ An iterable of chips in the machine

        :return: An iterable of chips
        :rtype: iterable of :py:class:`spinn_machine.chip.Chip`
        :raise None: does not raise any known exceptions
        """
        return self._chips.itervalues()
    
    def __iter__(self):
        """ Get an iterable of the chip coordinates and chips
        
        :return: An iterable of tuples of ((x, y), chip) where:
                    * (x, y) is a tuple where:
                        * x is the x-coordinate of a chip
                        * y is the y-coordinate of a chip
                    * chip is a chip
        :rtype: iterable of ((int, int), :py:class:`spinn_machine.chip.Chip`)
        :raise None: does not raise any known exceptions
        """
        return self._chips.iteritems()

    def get_chip_at(self, x, y):
        """ Get the chip at a specific (x, y) location.\
            Also implemented as __getitem__((x, y))

        :param x: the x-coordinate of the requested chip
        :type x: int
        :param y: the y-coordinate of the requested chip
        :type y: int
        :return: the chip at the specified location, or None if no such chip
        :rtype: :py:class:`spinn_machine.chip.Chip`
        :raise None: does not raise any known exceptions
        """
        chip_id = (x, y)
        if chip_id in self._chips:
            return self._chips[chip_id]
        return None
    
    def __getitem__(self, x_y_tuple):
        """ Get the chip at a specific (x, y) location
        
        :param x_y_tuple: A tuple of (x, y) where:
                    * x is the x-coordinate of the chip to retrieve
                    * y is the y-coordinate of the chip to retrieve
        :type x_y_tuple: (int, int)
        :return: the chip at the specified location, or None if no such chip
        :rtype: :py:class:`spinn_machine.chip.Chip`
        :raise None: does not raise any known exceptions
        """
        x, y = x_y_tuple
        return self.get_chip_at(x, y)
    
    def is_chip_at(self, x, y):
        """ Determine if a chip exists at the given coordinates.\
            Also implemented as __contains__((x, y))

        :param x: x location of the chip to test for existence
        :type x: int
        :param y: y location of the chip to test for existence
        :type y: int
        :return: True if the chip exists, False otherwise
        :rtype: bool
        :raise None: does not raise any known exceptions
        """
        chip_id = (x, y)
        return chip_id in self._chips
    
    def __contains__(self, x_y_tuple):
        """ Determine if a chip exists at the given coordinates

        :param x_y_tuple: A tuple of (x, y) where:
                    * x is the x-coordinate of the chip to retrieve
                    * y is the y-coordinate of the chip to retrieve
        :type x_y_tuple: (int, int)
        :return: True if the chip exists, False otherwise
        :rtype: bool
        :raise None: does not raise any known exceptions
        """
        x, y = x_y_tuple
        return self.is_chip_at(x, y)
    
    @property
    def max_chip_x(self):
        """ The maximum x-coordinate of any chip in the board
        
        :return: The maximum x-coordinate
        :rtype: int
        """
        return self._max_chip_x
    
    @property
    def max_chip_y(self):
        """ The maximum y-coordinate of any chip in the board
        
        :return: The maximum y-coordinate
        :rtype: int
        """
        return self._max_chip_y
    
    @property
    def ethernet_connected_chips(self):
        """ The chips in the machine that have an ethernet connection
        
        :return: An iterable of chips
        :rtype: iterable of :py:class:`spinn_machine.chip.Chip`
        """
        return self._ethernet_connected_chips

    def generate_radial_chips(
            self, resource_tracker=None, start_chip_x=0, start_chip_y=0,
            size_of_list=None):
        """

        :param resource_tracker: tracker of resoruces, to see if a chip exists
        :param start_chip_x: the start chip x postition to start radialing out
        from
        :type start_chip_x: int
        :param start_chip_y:the start chip y postition to start radialing out
        from
        :type start_chip_y: int
        :param size_of_list: the number of chips needed from the machine for
        the list
        :type size_of_list: int
        :return: a ordered set of chips radialling out from a given chip.
        """

        # if no size given, assume all machine is needed
        if size_of_list is None:
            size_of_list = len(self._chips)

        # locate first chip
        first_chip = self.get_chip_at(start_chip_x, start_chip_y)
        done_chips = set()
        found_chips = OrderedSet()
        search = deque([first_chip])
        while len(search) > 0 and len(found_chips) <= size_of_list:
            chip = search.pop()
            if (resource_tracker is None or
                    resource_tracker.is_chip_available(chip.x, chip.y)):
                found_chips.add(self.get_chip_at(chip.x, chip.y))
                done_chips.add(chip)

            # Examine the links of the chip to find the next chips
            for link in chip.router.links:
                next_chip = self.get_chip_at(link.destination_x,
                                             link.destination_y)

                # Don't search found chips again
                if next_chip not in done_chips:
                    search.appendleft(next_chip)
        return found_chips

    def get_cloest_chip_to(self, chip_x, chip_y):
        """
        gets the closest chip to a given chip coords
        :param chip_x: the chip coord in x axis for looking for cloest to
        :param chip_y: the chip coord in y axis for looking for cloest to
        :return:
        """
        if self.is_chip_at(chip_x, chip_y):
            return self.get_chip_at(chip_x, chip_y)
        else:
            searched_ids = set()
            pre_visited_chips = set()
            searched_ids.add("{}:{}".format(chip_x, chip_y))
            search = deque([(chip_x, chip_y)])
            found_chip = None
            while len(search) > 0 and found_chip is None:
                (chip_x, chip_y) = search.pop()
                pre_visited_chips.add((chip_x, chip_y))
                next_chips = self._locate_neighbouring_chips(chip_x, chip_y)
                for (next_chip_x, next_chip_y) in next_chips:
                    if (not self.is_chip_at(next_chip_x, next_chip_y) and
                            (next_chip_x, next_chip_y) not in pre_visited_chips):
                        search.appendleft((next_chip_x, next_chip_y))
                    else:
                        found_chip = self.get_chip_at(next_chip_x, next_chip_y)
        return found_chip

    def _locate_neighbouring_chips(self, chip_x, chip_y):
        """
        locates the chips which reside next to the input chip
        :param chip_x: the input chips x coordinate
        :param chip_y: the input chip y coordinate
        :return: a iterable of tuples containing x and y of neighbouring chips
        """
        next_chips = list()
        removal_chips = list()
        next_chips.append((chip_x + 1, chip_y))
        next_chips.append((chip_x + 1, chip_y + 1))
        next_chips.append((chip_x, chip_y + 1))
        next_chips.append((chip_x - 1, chip_y))
        next_chips.append((chip_x - 1, chip_y - 1))
        next_chips.append((chip_x, chip_y - 1))
        for (chip_id_x, chip_id_y) in next_chips:
            if (chip_id_x < 0 or chip_id_x > self._max_chip_x or
                    chip_id_y < 0 or chip_id_y > self._max_chip_y):
                removal_chips.append((chip_id_x, chip_id_y))
        for (chip_id_x, chip_id_y) in removal_chips:
            next_chips.remove((chip_id_x, chip_id_y))
        return next_chips

    def __str__(self):
        return "[Machine: max_x={}, max_y={}, chips={}]".format(
            self._max_chip_x, self._max_chip_y, self._chips.values())
        
    def __repr__(self):
        return self.__str__()

    def cores_and_link_output_string(self):
        """
        helper method for figuring the machine's detials
        :return:
        """
        cores = 0
        links = 0
        total_links = dict()
        for chip_key in self._chips.keys():
            chip = self._chips[chip_key]
            cores += len(list(chip.processors))
            for link in chip.router.links:
                key1 = "{}:{}:{}:{}".format(
                    link.source_x, link.source_y, link.destination_x,
                    link.destination_y)
                key2 = "{}:{}:{}:{}".format(
                    link.destination_x, link.destination_y, link.source_x,
                    link.source_y)
                if (key1 not in total_links.keys()
                        and key2 not in total_links.keys()):
                    total_links[key1] = key1
            links += len(total_links.keys())
        return "{} cores and {} links".format(cores, links)
