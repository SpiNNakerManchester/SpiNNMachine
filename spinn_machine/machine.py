
# spinn_machine imports
from spinn_machine.exceptions import SpinnMachineAlreadyExistsException
from spinn_machine.spinnaker_link_data import SpinnakerLinkData

# general imports
from collections import OrderedDict


class Machine(object):
    """ A Representation of a Machine with a number of Chips.  Machine is also\
        iterable, providing ((x, y), chip) where:

            * x is the x-coordinate of a chip
            * y is the y-coordinate of a chip
            * chip is the chip with the given x, y coordinates
    """

    __slots__ = [
        # max x id for the chips within the machine
        "_max_chip_x",

        # max y id for the chips wtihin the machine
        "_max_chip_y",

        # list of chips that are connected to ethernets
        "_ethernet_connected_chips",

        # dict of [(x,y)] -> list of chips
        "_chips_by_local_ethernet",

        # dict of [(spinnaker board address, spinnaker link id) -> spinnaker
        # link data object
        "_spinnaker_links",

        # ordered dict of [(x,y) -> chip
        "_chips",

        # the boot chip x coord (int)
        "_boot_x",

        # the boot cihip y coord (int)
        "_boot_y"
    ]

    # current opinions is that the Ethernet connected chip can handle 10
    # UDP packets per millisecond
    MAX_BANDWIDTH_PER_ETHERNET_CONNECTED_CHIP = 10 * 256

    # Table of the amount to add to the x and y coordinates to get the
    #  coordinates down the given link (0-5)
    LINK_ADD_TABLE = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]

    def __init__(self, chips, boot_x, boot_y):
        """
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`spinn_machine.chip.Chip`
        :param boot_x: The x-coordinate of the chip used to boot the machine
        :param boot_y: The y-coordinate of the chip used to boot the machine
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    any two chips have the same x and y coordinates
        """

        # The maximum chip x coordinate
        self._max_chip_x = 0

        # The maximum chip y coordinate
        self._max_chip_y = 0

        # The list of chips with Ethernet connections
        self._ethernet_connected_chips = list()

        # The dictionary of chips via their nearest Ethernet connected chip
        self._chips_by_local_ethernet = dict()

        # The dictionary of spinnaker links by "id" (int)
        self._spinnaker_links = dict()

        # The dictionary of chips
        self._chips = OrderedDict()
        self.add_chips(chips)

        # Store the boot chip information
        self._boot_x = boot_x
        self._boot_y = boot_y

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

        chip_id = (chip.nearest_ethernet_x, chip.nearest_ethernet_y)
        if chip_id not in self._chips_by_local_ethernet:
            self._chips_by_local_ethernet[chip_id] = list()
        self._chips_by_local_ethernet[chip_id].append(chip)

    def get_chips_via_local_ethernet(self, local_ethernet_x, local_ethernet_y):
        """
        returns a list of chips which have the nearest Ethernet chip of x and y
        :param local_ethernet_x: the Ethernet chip x coord
        :param local_ethernet_y: the Ethernet chip y coord
        :return: list of chips
        """
        chip_id = (local_ethernet_x, local_ethernet_y)
        if chip_id not in self._chips_by_local_ethernet:
            return []
        else:
            return self._chips_by_local_ethernet[chip_id]

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
    def n_chips(self):
        """

        :return:
        """
        return len(self._chips)

    @property
    def ethernet_connected_chips(self):
        """ The chips in the machine that have an Ethernet connection

        :return: An iterable of chips
        :rtype: iterable of :py:class:`spinn_machine.chip.Chip`
        """
        return self._ethernet_connected_chips

    def add_spinnaker_link(self, spinnaker_link):
        """ Add a spinnaker link to the machine
        """
        if spinnaker_link.spinnaker_link_id in self._spinnaker_links:
            raise SpinnMachineAlreadyExistsException(
                "spinnaker_link", spinnaker_link.spinnaker_link_id)
        self._spinnaker_links[
            spinnaker_link.spinnaker_link_id] = spinnaker_link

    @property
    def spinnaker_links(self):
        """ The set of spinnaker links in the machine

        :return: An iterable of spinnaker links
        :rtype: iterable of\
            :py:class:`spinn_machine.spinnaker_link_data.SpinnakerLinkData`
        """
        return self._spinnaker_links.values()

    def get_spinnaker_link_with_id(self, spinnaker_link_id):
        """ Get a spinnaker link with a given id

        :param spinnaker_link_id: The id of the link
        :type spinnaker_link_id: int
        :rtype: :py:class:`spinn_machine.spinnaker_link_data.SpinnakerLinkData`
        """
        return self._spinnaker_links[spinnaker_link_id]

    @staticmethod
    def get_chip_over_link(x, y, link, width, height):
        """ Get the x and y coordinates of the chip over the given link

        :param x: The x coordinate of the chip to start from
        :param y: The y coordinate of the chip to start from
        :param link: The id of the link to traverse, between 0 and 5
        :param width: The width of the machine being considered
        :param height: The height of the machine being considered
        """
        add_x, add_y = Machine.LINK_ADD_TABLE[link]
        link_x = (x + add_x + width) % width
        link_y = (y + add_y + height) % height
        return link_x, link_y

    def locate_spinnaker_links(self, version_no):
        """ Gets SpiNNaker links that are on a given machine depending on the\
            version of the board.

        :param version_no: which version of board to use
        :param machine: the machine to detect the links of
        :return: A SpiNNakerLink object
        :raises: SpinnMachineInvalidParameterException when:
            1. in valid spinnaker link value
            2. invalid version number
            3. uses wrap arounds
        """
        spinnaker_links = list()
        if version_no == 3 or version_no == 2:
            chip = self.get_chip_at(0, 0)
            if not chip.router.is_link(3):
                spinnaker_links.append(SpinnakerLinkData(0, 0, 0, 3))
            chip = self.get_chip_at(1, 0)
            if not chip.router.is_link(0):
                spinnaker_links.append(SpinnakerLinkData(1, 1, 0, 0))
        elif version_no == 4 or version_no == 5:
            chip = self.get_chip_at(0, 0)
            if not chip.router.is_link(4):
                spinnaker_links.append(SpinnakerLinkData(0, 0, 0, 4))
        return spinnaker_links

    def __str__(self):
        return "[Machine: max_x={}, max_y={}, chips={}]".format(
            self._max_chip_x, self._max_chip_y, self._chips.values())

    def __repr__(self):
        return self.__str__()

    def get_cores_and_link_count(self):
        """ Get the number of cores and links from the machine

        :return: tuple of (n_cores, n_links)
        """
        cores = 0
        total_links = dict()
        for chip_key in self._chips:
            chip = self._chips[chip_key]
            cores += len(list(chip.processors))
            for link in chip.router.links:
                key1 = (link.source_x, link.source_y, link.source_link_id)
                key2 = (link.destination_x, link.destination_y,
                        link.multicast_default_from)
                if key1 not in total_links and key2 not in total_links:
                    total_links[key1] = key1
        links = len(total_links.keys())
        return cores, links

    def cores_and_link_output_string(self):
        """ Get a string detailing the number of cores and links

        :rtype: str
        """
        cores, links = self.get_cores_and_link_count()
        return "{} cores and {} links".format(cores, links)

    @property
    def boot_x(self):
        """ The x-coordinate of the chip used to boot the machine

        :rtype: int
        """
        return self._boot_x

    @property
    def boot_y(self):
        """ The y-coordinate of the chip used to boot the machine

        :rtype: int
        """
        return self._boot_y

    @property
    def boot_chip(self):
        """ The chip used to boot the machine

        :rtype: `py:class:spinn_machine.chip.Chip`
        """
        return self._chips[(self._boot_x, self._boot_y)]
