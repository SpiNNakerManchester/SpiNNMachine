from spinn_machine.exceptions import SpinnMachineAlreadyExistsException
from collections import OrderedDict

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
            raise SpinnMachineAlreadyExistsException(
                    "chip", "{}, {}".format(chip.x, chip.y))
        
        self._chips[chip_id] = chip
        
        if chip.x > self._max_chip_x:
            self._max_chip_x = chip.x
        if chip.y > self._max_chip_y:
            self._max_chip_y = chip.y

    def add_chips(self, chips):
        """ Add some chips to the machine
        
        :param chips: an iterable of chips
        :type chips: iterable of :py:class:`spinn_machine.chip.Chip`
        :return: Nothing is returned
        :rtype: None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    a chip with the same x and y coordinates as one being added\
                    already exists
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
