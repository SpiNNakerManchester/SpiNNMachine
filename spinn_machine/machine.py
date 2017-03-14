
# spinn_machine imports
from spinn_machine import exceptions
from spinn_machine.link_data_objects.fpga_link_data import FPGALinkData
from spinn_machine.core_subsets import CoreSubsets
from spinn_machine.link_data_objects.spinnaker_link_data \
    import SpinnakerLinkData

# general imports
from collections import OrderedDict


class Machine(object):
    """ A Representation of a Machine with a number of Chips.  Machine is also\
        iterable, providing ((x, y), chip) where:

            * x is the x-coordinate of a chip
            * y is the y-coordinate of a chip
            * chip is the chip with the given x, y coordinates
    """

    # current opinions is that the Ethernet connected chip can handle 10
    # UDP packets per millisecond
    MAX_BANDWIDTH_PER_ETHERNET_CONNECTED_CHIP = 10 * 256

    # Table of the amount to add to the x and y coordinates to get the
    #  coordinates down the given link (0-5)
    LINK_ADD_TABLE = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]

    BOARD_48_CHIP_GAPS = {
        (0, 4), (0, 5), (0, 6), (0, 7), (1, 5), (1, 6), (1, 7), (2, 6), (2, 7),
        (3, 7), (5, 0), (6, 0), (6, 1), (7, 0), (7, 1), (7, 2)
    }

    __slots__ = (
        "_boot_x",
        "_boot_y",
        "_boot_ethernet_address",
        "_chips",
        "_ethernet_connected_chips",
        "_fpga_links",
        "_max_chip_x",
        "_max_chip_y",
        "_spinnaker_links",
        "_maximum_user_cores_on_chip"
    )

    def __init__(self, chips, boot_x, boot_y):
        """
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`spinn_machine.chip.Chip`
        :param boot_x: The x-coordinate of the chip used to boot the machine
        :type boot_x: int
        :param boot_y: The y-coordinate of the chip used to boot the machine
        :type boot_y: int
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: If\
                    any two chips have the same x and y coordinates
        """

        # The maximum chip x coordinate
        self._max_chip_x = 0

        # The maximum chip y coordinate
        self._max_chip_y = 0

        # The maximum number of user cores on any chip
        self._maximum_user_cores_on_chip = 0

        # The list of chips with Ethernet connections
        self._ethernet_connected_chips = list()

        # The dictionary of spinnaker links by board address and "id" (int)
        self._spinnaker_links = dict()

        # The dictionary of FPGA links by board address, FPGA and link id
        self._fpga_links = dict()

        # Store the boot chip information
        self._boot_x = boot_x
        self._boot_y = boot_y
        self._boot_ethernet_address = None

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
            raise exceptions.SpinnMachineAlreadyExistsException(
                "chip", "{}, {}".format(chip.x, chip.y))

        self._chips[chip_id] = chip

        if chip.x > self._max_chip_x:
            self._max_chip_x = chip.x
        if chip.y > self._max_chip_y:
            self._max_chip_y = chip.y

        if chip.ip_address is not None:
            self._ethernet_connected_chips.append(chip)
            if (chip.x == self._boot_x) and (chip.y == self._boot_y):
                self._boot_ethernet_address = chip.ip_address

        if chip.n_user_processors > self._maximum_user_cores_on_chip:
            self._maximum_user_cores_on_chip = chip.n_user_processors

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

    @property
    def chip_coordinates(self):
        """ An iterable of chip coordinates in the machine

        :return: An iterable of chip coordinates
        :rtype: iterable of (int, int)
        """
        return self._chips.iterkeys()

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
        return (x, y) in self._chips

    def is_link_at(self, x, y, link):
        """ Determine if a link exists at the given coordinates

        :param x: The x location of the chip to test the link of
        :type x: int
        :param y: The y location of the chip to test the link of
        :type y: int
        :param link: The link to test the existence of
        :type link: int
        """
        return (x, y) in self._chips and self._chips[x, y].router.is_link(link)

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
        return len(self._chips)

    @property
    def ethernet_connected_chips(self):
        """ The chips in the machine that have an Ethernet connection

        :return: An iterable of chips
        :rtype: iterable of :py:class:`spinn_machine.chip.Chip`
        """
        return self._ethernet_connected_chips

    @property
    def spinnaker_links(self):
        """ The set of spinnaker links in the machine

        :return: An iterable of spinnaker links
        :rtype: iterable of\
            :py:class:`spinn_machine.spinnaker_link_data.SpinnakerLinkData`
        """
        return self._spinnaker_links.iteritems()

    def get_spinnaker_link_with_id(
            self, spinnaker_link_id, board_address=None):
        """ Get a spinnaker link with a given id

        :param spinnaker_link_id: The id of the link
        :type spinnaker_link_id: int
        :param board_address:\
            the board address that this spinnaker link is associated with
        :type board_address: str or None
        :return: The spinnaker link data or None if no link
        :rtype:\
            :py:class:`spinn_machine.link_data_objects.spinnaker_link_data.SpinnakerLinkData`
        """
        if board_address is None:
            board_address = self._boot_ethernet_address
        return self._spinnaker_links.get(
            (board_address, spinnaker_link_id), None)

    def get_fpga_link_with_id(self, fpga_id, fpga_link_id, board_address=None):
        """ Get an FPGA link data item that corresponds to the FPGA and FPGA\
            link for a given board address.

        :param fpga_id:\
            the id of the FPGA that the data is going through.  Refer to \
            technical document located here for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :type fpga_link_id: int
        :param fpga_link_id:\
            the link id of the FPGA. Refer to technical document located here\
            for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :type fpga_id: int
        :param board_address:\
            the board address that this spinnaker link is associated with
        :type board_address: str
        :rtype:\
            :py:class:`spinn_machine.link_data_objects.fpga_link_data.FPGALinkData`
        :return: the given FPGA link object or None if no such link
        """
        if board_address is None:
            board_address = self._boot_ethernet_address
        return self._fpga_links.get(
            (board_address, fpga_id, fpga_link_id), None)

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

    def add_spinnaker_links(self, version_no):
        """ Add SpiNNaker links that are on a given machine depending on the\
            version of the board.

        :param version_no: which version of board to use
        """
        if version_no == 3 or version_no == 2:
            chip_0_0 = self.get_chip_at(0, 0)
            if not chip_0_0.router.is_link(3):
                self._spinnaker_links[chip_0_0.ip_address, 0] = \
                    SpinnakerLinkData(0, 0, 0, 3, chip_0_0.ip_address)
            chip = self.get_chip_at(1, 0)
            if not chip.router.is_link(0):
                self._spinnaker_links[chip_0_0.ip_address, 1] = \
                    SpinnakerLinkData(1, 1, 0, 0, chip_0_0.ip_address)
        elif version_no == 4 or version_no == 5 or version_no is None:
            for chip in self._ethernet_connected_chips:
                if not chip.router.is_link(4):
                    self._spinnaker_links[
                        chip.ip_address, 0] = SpinnakerLinkData(
                            0, chip.x, chip.y, 4, chip.ip_address)

    def add_fpga_links(self, version_no):
        """ Add FPGA links that are on a given machine depending on the\
            version of the board.

        :param version_no: which version of board to use
        """
        if version_no == 4 or version_no == 5 or version_no is None:

            for ethernet_connected_chip in self._ethernet_connected_chips:

                # the side of the hexagon shape of the board are as follows
                #
                #
                #                 North
                #                 ####
                #                #####
                #  Left North   ###### Right
                #              #######
                #             ########
                #             #######
                #    Left     ###### Right South
                #             #####
                #             South
                #
                chips = {
                    'left': [], 'left_north': [], 'north': [],
                    'right': [], 'right_south': [], 'south': []
                }

                # handle the first chip
                x = ethernet_connected_chip.x
                y = ethernet_connected_chip.y
                ip = ethernet_connected_chip.ip_address

                # handle left chips (goes up 4)
                chips['left'].append((x, y))
                for _ in range(0, 3):
                    y = (y + 1) % (self._max_chip_y + 1)
                    chips['left'].append((x, y))

                # handle left north (goes across 4 but add this chip)
                chips['left_north'].append((x, y))
                for _ in range(0, 4):
                    x = (x + 1) % (self._max_chip_x + 1)
                    y = (y + 1) % (self._max_chip_y + 1)
                    chips['left_north'].append((x, y))

                # handle north (goes left 3 but add this chip)
                chips['north'].append((x, y))
                for _ in range(0, 3):
                    x = (x + 1) % (self._max_chip_x + 1)
                    chips['north'].append((x, y))

                # handle east (goes down 4 but add this chip)
                chips['right'].append((x, y))
                for _ in range(0, 4):
                    y = (y - 1) % (self._max_chip_y + 1)
                    chips['right'].append((x, y))

                # handle east south (goes down across 3 but add this chip)
                chips['right_south'].append((x, y))
                for _ in range(0, 3):
                    x = (x - 1) % (self._max_chip_x + 1)
                    y = (y - 1) % (self._max_chip_y + 1)
                    chips['right_south'].append((x, y))

                # handle south (goes across 3 but add this chip)
                chips['south'].append((x, y))
                for _ in range(0, 4):
                    x = (x - 1) % (self._max_chip_x + 1)
                    chips['south'].append((x, y))

                # handle left
                fpga_id = 1
                fpga_link = 0
                for x, y in chips['left']:
                    self._add_fpga_link(fpga_id, fpga_link, x, y, 4, ip)
                    fpga_link += 1
                    self._add_fpga_link(fpga_id, fpga_link, x, y, 3, ip)
                    fpga_link += 1

                # handle left north
                first = chips['left_north'][0]
                last = chips['left_north'][-1]
                for x, y in chips['left_north']:
                    if (x, y) == first:
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 2, ip)
                        fpga_link += 1
                    elif (x, y) == last:
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 3, ip)
                        fpga_link += 1
                    else:
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 3, ip)
                        fpga_link += 1
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 2, ip)
                        fpga_link += 1

                # handle north
                fpga_id = 2
                fpga_link = 0
                for x, y in chips['north']:
                    self._add_fpga_link(fpga_id, fpga_link, x, y, 2, ip)
                    fpga_link += 1
                    self._add_fpga_link(fpga_id, fpga_link, x, y, 1, ip)
                    fpga_link += 1

                # handle right
                first = chips['right'][0]
                last = chips['right'][-1]
                for x, y in chips['right']:
                    if (x, y) == first:
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 0, ip)
                        fpga_link += 1
                    elif (x, y) == last:
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 1, ip)
                        fpga_link += 1
                    else:
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 1, ip)
                        fpga_link += 1
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 0, ip)
                        fpga_link += 1

                # handle right south
                fpga_id = 0
                fpga_link = 0
                for x, y in chips['right_south']:
                    self._add_fpga_link(fpga_id, fpga_link, x, y, 0, ip)
                    fpga_link += 1
                    self._add_fpga_link(fpga_id, fpga_link, x, y, 5, ip)
                    fpga_link += 1

                # handle south
                first = chips['south'][0]
                last = chips['south'][-1]
                for x, y in chips['south']:
                    if (x, y) == first:
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 4, ip)
                        fpga_link += 1
                    elif (x, y) == last:
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 5, ip)
                        fpga_link += 1
                    else:
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 5, ip)
                        fpga_link += 1
                        self._add_fpga_link(fpga_id, fpga_link, x, y, 4, ip)
                        fpga_link += 1

    def _add_fpga_link(self, fpga_id, fpga_link, x, y, link, board_address):
        if self.is_chip_at(x, y):
            if not self.is_link_at(x, y, link):
                self._fpga_links[board_address, fpga_id, fpga_link] = \
                    FPGALinkData(
                        fpga_link_id=fpga_link, fpga_id=fpga_id,
                        connected_chip_x=x, connected_chip_y=y,
                        connected_link=link, board_address=board_address)

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

    def get_chips_on_board(self, chip):
        """ Get the chips that are on the same board as the given chip

        :param chip: The chip to find other chips on the same board as
        :return: An iterable of (x, y) coordinates of chips on the same board
        """
        eth_x = chip.nearest_ethernet_x
        eth_y = chip.nearest_ethernet_y
        for chip_x, chip_y in zip(range(0, 8), range(0, 8)):
            x = eth_x + chip_x
            y = eth_y + chip_y
            if (self.is_chip_at(x, y) and
                    (x, y) not in Machine.BOARD_48_CHIP_GAPS):
                yield x, y

    def reserve_system_processors(self):
        """ Sets one of the none monitor system processors as a system\
            processor on every Chip

        Updates maximum_user_cores_on_chip

        :return:\
            A CoreSubsets of reserved cores, and a list of (x, y) of chips\
            where a non-system core was not available
        :rtype:\
            (:py:class:`spinn_machine.core_subsets.CoreSubsets`,\
            list of (int, int))
        """
        self._maximum_user_cores_on_chip = 0
        reserved_cores = CoreSubsets()
        failed_chips = list()
        for chip in self._chips.itervalues():

            # Try to get a new system processor
            core_reserved = chip.reserve_a_system_processor()
            if core_reserved is None:
                failed_chips.append((chip.x, chip.y))
            else:
                reserved_cores.add_processor(chip.x, chip.y, core_reserved)

            # Update the maximum user cores either way
            if (chip.n_user_processors > self._maximum_user_cores_on_chip):
                self._maximum_user_cores_on_chip = chip.n_user_processors

        return reserved_cores, failed_chips

    @property
    def maximum_user_cores_on_chip(self):
        """ The maximum number of user cores on any chip
        """
        return self._maximum_user_cores_on_chip
