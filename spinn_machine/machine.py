try:
    from collections.abc import OrderedDict
except ImportError:
    from collections import OrderedDict
from six import iteritems, iterkeys, itervalues, add_metaclass
from .exceptions import (SpinnMachineAlreadyExistsException,
                         SpinnMachineInvalidParameterException)
from spinn_machine.link_data_objects import FPGALinkData, SpinnakerLinkData
from spinn_utilities.abstract_base import (
    AbstractBase, abstractproperty, abstractmethod)


@add_metaclass(AbstractBase)
class Machine(object):
    """ A representation of a SpiNNaker Machine with a number of Chips.\
        Machine is also iterable, providing ((x, y), chip) where:

            * x is the x-coordinate of a chip
            * y is the y-coordinate of a chip
            * chip is the chip with the given x, y coordinates
    """

    # current opinions is that the Ethernet connected chip can handle 10
    # UDP packets per millisecond
    MAX_BANDWIDTH_PER_ETHERNET_CONNECTED_CHIP = 10 * 256
    MAX_CORES_PER_CHIP = 18
    MAX_CHIPS_PER_48_BOARD = 48
    MAX_CHIPS_PER_4_CHIP_BOARD = 4
    BOARD_VERSION_FOR_48_CHIPS = [4, 5]
    BOARD_VERSION_FOR_4_CHIPS = [2, 3]

    # other useful magic numbers for machines
    MAX_CHIP_X_ID_ON_ONE_BOARD = 7
    MAX_CHIP_Y_ID_ON_ONE_BOARD = 7
    SIZE_X_OF_ONE_BOARD = 8
    SIZE_Y_OF_ONE_BOARD = 8

    # Table of the amount to add to the x and y coordinates to get the
    #  coordinates down the given link (0-5)
    LINK_ADD_TABLE = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]

    BOARD_48_CHIPS = [
        (0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
        (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 0), (3, 1), (3, 2),
        (3, 3), (3, 4), (3, 5), (3, 6), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4),
        (4, 5), (4, 6), (4, 7), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
        (5, 7), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (7, 3), (7, 4),
        (7, 5), (7, 6), (7, 7)
    ]

    __slots__ = (
        "_boot_x",
        "_boot_y",
        "_boot_ethernet_address",
        "_chips",
        "_ethernet_connected_chips",
        "_fpga_links",
        "_height",
        "_max_chip_x",
        "_max_chip_y",
        "_spinnaker_links",
        "_maximum_user_cores_on_chip",
        "_virtual_chips",
        "_width"
    )

    def __init__(self, width, height, chips, boot_x, boot_y):
        """
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`~spinn_machine.Chip`
        :param boot_x: The x-coordinate of the chip used to boot the machine
        :type boot_x: int
        :param boot_y: The y-coordinate of the chip used to boot the machine
        :type boot_y: int
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If any two chips have the same x and y coordinates
        """

        self._width = width
        self._height = height

        # The maximum chip x coordinate
        self._max_chip_x = 0

        # The maximum chip y coordinate
        self._max_chip_y = 0

        # The maximum number of user cores on any chip
        self._maximum_user_cores_on_chip = 0

        # The list of chips with Ethernet connections
        self._ethernet_connected_chips = list()

        # The dictionary of SpiNNaker links by board address and "ID" (int)
        self._spinnaker_links = dict()

        # The dictionary of FPGA links by board address, FPGA and link ID
        self._fpga_links = dict()

        # Store the boot chip information
        self._boot_x = boot_x
        self._boot_y = boot_y
        self._boot_ethernet_address = None

        # The dictionary of chips
        self._chips = OrderedDict()
        self.add_chips(chips)

        self._virtual_chips = list()

    @abstractmethod
    def x_y_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the protential x,y locations of all the chips on the board #
        with this ethernet. Including the Ethernet chip itself.

        Wraparounds are handled as appropriate.

        Note: This method does not check if the chip actually exists as is
        intended to be called to create the chips.

        Warning: GIGO! This methods assumes that ethernet_x and ethernet_y are
        the local 0,0 of an existing board,
        within the width and height of the machine.

        :param ethernet_x: The x coordinate of a (local 0,0) legal ethernet
        chip
        :param ethernet_y: The x coordinate of a (local 0,0) legal ethernet
        chip
        :return: Yeilds the (x, Y) coordinated of all the protential chips on
         this board.
        """

    @abstractmethod
    def x_y_over_link(self, x, y, link):
        """
        Get the protential x,y location of the chip reached over this link.

        Wraparounds are handled as appropriate.

        Note: This method does not check if either chip source or destination
        actually exists as is intended to be called to create the links.

        It is the callers responsibility to check the validity of this call
        before making it or the validty of the result.

        Warning: GIGO! This methods assumes that x and y are within the
        width and height of the machine, and that the link goes to another
        chip on the machine.

        On machine without full wraparound it is possible that this method
        generates x_Y values that fall outside of the legal values including
        negatives values, x = width or y = height.

        :param x: The x coordinate of a chip that will exist on the machine
        :param y: The x coordinate of a chip that will exist on the machine
        :param link: The link to another chip that could exist on the machine
        :return: x and y coordinates of the chip over that link if it is valid
        or some fictional x y if not.
        """

    def add_chip(self, chip):
        """ Add a chip to the machine

        :param chip: The chip to add to the machine
        :type chip: :py:class:`~spinn_machine.Chip`
        :return: Nothing is returned
        :rtype: None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If a chip with the same x and y coordinates already exists
        """
        chip_id = (chip.x, chip.y)
        if chip_id in self._chips:
            raise SpinnMachineAlreadyExistsException(
                "chip", "{}, {}".format(chip.x, chip.y))

        if not chip.virtual:
            if chip.x >= self._width:
                raise SpinnMachineInvalidParameterException("chip", chip,
                    "x to high for machine with width {}".format(self._width))
            if chip.y >= self._height:
                raise SpinnMachineInvalidParameterException("chip", chip,
                    "y to high for machine with height {}".format(self._height))
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

    def add_virtual_chip(self, chip):
        self._virtual_chips.append(chip)
        self.add_chip(chip)

    def add_chips(self, chips):
        """ Add some chips to the machine

        :param chips: an iterable of chips
        :type chips: iterable(:py:class:`~spinn_machine.Chip`)
        :return: Nothing is returned
        :rtype: None
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If a chip with the same x and y coordinates as one being added\
            already exists
        """
        for next_chip in chips:
            self.add_chip(next_chip)

    @property
    def chips(self):
        """ An iterable of chips in the machine

        :return: An iterable of chips
        :rtype: iterable(:py:class:`~spinn_machine.Chip`)
        :raise None: does not raise any known exceptions
        """
        return itervalues(self._chips)

    @property
    def chip_coordinates(self):
        """ An iterable of chip coordinates in the machine

        :return: An iterable of chip coordinates
        :rtype: iterable(int,int)
        """
        return iterkeys(self._chips)

    def __iter__(self):
        """ Get an iterable of the chip coordinates and chips

        :return: An iterable of tuples of ((x, y), chip) where:
            * (x, y) is a tuple where:
                * x is the x-coordinate of a chip
                * y is the y-coordinate of a chip
            * chip is a chip
        :rtype: iterable((int, int), :py:class:`~spinn_machine.Chip`)
        :raise None: does not raise any known exceptions
        """
        return iteritems(self._chips)

    def __len__(self):
        """ Get the total number of chips.

        :return: The number of items in the underlying iterable
        :rtype: int
        """
        return len(self._chips)

    def get_chip_at(self, x, y):
        """ Get the chip at a specific (x, y) location.\
            Also implemented as __getitem__((x, y))

        :param x: the x-coordinate of the requested chip
        :type x: int
        :param y: the y-coordinate of the requested chip
        :type y: int
        :return: the chip at the specified location, or None if no such chip
        :rtype: :py:class:`~spinn_machine.Chip`
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
        :rtype: :py:class:`~spinn_machine.Chip`
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
        :type x_y_tuple: tuple(int, int)
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
    def width(self):
        """ The width to the machine ignoring virtual chips

        :return: The width to the machine ignoring virtual chips
        :rtype: int
        """
        return self._width

    @property
    def height(self):
        """ The height to the machine ignoring virtual chips

        :return: The height to the machine ignoring virtual chips
        :rtype: int
        """
        return self._height


    @property
    def n_chips(self):
        return len(self._chips)

    @property
    def ethernet_connected_chips(self):
        """ The chips in the machine that have an Ethernet connection

        :return: An iterable of chips
        :rtype: iterable of :py:class:`~spinn_machine.Chip`
        """
        return self._ethernet_connected_chips

    @property
    def spinnaker_links(self):
        """ The set of SpiNNaker links in the machine

        :return: An iterable of SpiNNaker links
        :rtype: iterable of\
            :py:class:`~spinn_machine.link_data_objects.SpinnakerLinkData`
        """
        return iteritems(self._spinnaker_links)

    def get_spinnaker_link_with_id(
            self, spinnaker_link_id, board_address=None):
        """ Get a SpiNNaker link with a given ID

        :param spinnaker_link_id: The ID of the link
        :type spinnaker_link_id: int
        :param board_address:\
            the board address that this SpiNNaker link is associated with
        :type board_address: str or None
        :return: The SpiNNaker link data or None if no link
        :rtype:\
            :py:class:`~spinn_machine.link_data_objects.SpinnakerLinkData`
        """
        if board_address is None:
            board_address = self._boot_ethernet_address
        return self._spinnaker_links.get(
            (board_address, spinnaker_link_id), None)

    def get_fpga_link_with_id(self, fpga_id, fpga_link_id, board_address=None):
        """ Get an FPGA link data item that corresponds to the FPGA and FPGA\
            link for a given board address.

        :param fpga_id:\
            the ID of the FPGA that the data is going through.  Refer to \
            technical document located here for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :type fpga_link_id: int
        :param fpga_link_id:\
            the link ID of the FPGA. Refer to technical document located here\
            for more detail:
            https://drive.google.com/file/d/0B9312BuJXntlVWowQlJ3RE8wWVE
        :type fpga_id: int
        :param board_address:\
            the board address that this FPGA link is associated with
        :type board_address: str
        :rtype:\
            :py:class:`~spinn_machine.link_data_objects.FPGALinkData`
        :return: the given FPGA link object or None if no such link
        """
        if board_address is None:
            board_address = self._boot_ethernet_address
        return self._fpga_links.get(
            (board_address, fpga_id, fpga_link_id), None)

   def add_spinnaker_links(self, version_no):
        """ Add SpiNNaker links that are on a given machine depending on the\
            version of the board.

        :param version_no: which version of board to use
        """
        if version_no in self.BOARD_VERSION_FOR_4_CHIPS:
            chip_0_0 = self.get_chip_at(0, 0)
            if not chip_0_0.router.is_link(3):
                self._spinnaker_links[chip_0_0.ip_address, 0] = \
                    SpinnakerLinkData(0, 0, 0, 3, chip_0_0.ip_address)
            chip = self.get_chip_at(1, 0)
            if not chip.router.is_link(0):
                self._spinnaker_links[chip_0_0.ip_address, 1] = \
                    SpinnakerLinkData(1, 1, 0, 0, chip_0_0.ip_address)
        elif (version_no in self.BOARD_VERSION_FOR_48_CHIPS or
                version_no is None):
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
        if (version_no in self.BOARD_VERSION_FOR_48_CHIPS or
                version_no is None):

            for ethernet_connected_chip in self._ethernet_connected_chips:

                # the sides of the hexagonal shape of the board are as follows
                #
                #
                #                 Top
                #                 ####
                #                #####
                #  Top Left     ###### Right
                #              #######
                #             ########
                #             #######
                #    Left     ###### Bottom Right
                #             #####
                #             Bottom
                #

                # handle the first chip
                ex = ethernet_connected_chip.x
                ey = ethernet_connected_chip.y
                ip = ethernet_connected_chip.ip_address

                # List of x, y, l1, l2, dx, dy where:
                #     x = start x
                #     y = start y
                #     l1 = first link
                #     l2 = second link
                #     dx = change in x to next
                #     dy = change in y to next
                chip_links = [(7, 3, 0, 5, -1, -1),  # Bottom Right
                              (4, 0, 4, 5, -1, 0),   # Bottom
                              (0, 0, 4, 3, 0, 1),    # Left
                              (0, 3, 2, 3, 1, 1),    # Top Left
                              (4, 7, 2, 1, 1, 0),    # Top
                              (7, 7, 0, 1, 0, -1)]   # Right

                f = 0
                lk = 0
                for i, (x, y, l1, l2, dx, dy) in enumerate(chip_links):
                    for _ in range(4):
                        fx = (x + ex) % (self._max_chip_x + 1)
                        fy = (y + ey) % (self._max_chip_y + 1)
                        self._add_fpga_link(f, lk, fx, fy, l1, ip)
                        f, lk = self._next_fpga_link(f, lk)
                        if i % 2 == 1:
                            x += dx
                            y += dy
                        fx = (x + ex) % (self._max_chip_x + 1)
                        fy = (y + ey) % (self._max_chip_y + 1)
                        self._add_fpga_link(f, lk, fx, fy, l2, ip)
                        f, lk = self._next_fpga_link(f, lk)
                        if i % 2 == 0:
                            x += dx
                            y += dy

    # pylint: disable=too-many-arguments
    def _add_fpga_link(self, fpga_id, fpga_link, x, y, link, board_address):
        if self.is_chip_at(x, y) and not self.is_link_at(x, y, link):
            self._fpga_links[board_address, fpga_id, fpga_link] = \
                FPGALinkData(
                    fpga_link_id=fpga_link, fpga_id=fpga_id,
                    connected_chip_x=x, connected_chip_y=y,
                    connected_link=link, board_address=board_address)

    @staticmethod
    def _next_fpga_link(fpga_id, fpga_link):
        if fpga_link == 15:
            return fpga_id + 1, 0
        return fpga_id, fpga_link + 1

    def __str__(self):
        return "[Machine: max_x={}, max_y={}, n_chips={}]".format(
            self._max_chip_x, self._max_chip_y, self.n_chips)

    def __repr__(self):
        return self.__str__()

    def get_cores_and_link_count(self):
        """ Get the number of cores and links from the machine

        :return: tuple of (n_cores, n_links)
        :rtype: tuple(int,int)
        """
        cores = 0
        total_links = dict()
        for chip_key in self._chips:
            chip = self._chips[chip_key]
            cores += chip.n_processors
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

        :rtype: `~py:class:spinn_machine.Chip`
        """
        return self._chips[self._boot_x, self._boot_y]

    def get_chips_on_board(self, chip):
        """ Get the chips that are on the same board as the given chip

        :param chip: The chip to find other chips on the same board as
        :return: An iterable of (x, y) coordinates of chips on the same board
        :rtype: iterable(tuple(int,int))
        """
        if self._max_chip_x == 1:
            for x in range(0, 2):
                for y in range(0, 2):
                    if (self.is_chip_at(x, y)):
                        yield x, y
        else:
            eth_x = chip.nearest_ethernet_x
            eth_y = chip.nearest_ethernet_y
            for (chip_x, chip_y) in self.BOARD_48_CHIPS:
                if self.has_wrap_arounds:
                    x = (eth_x + chip_x) % (self._max_chip_x + 1)
                    y = (eth_y + chip_y) % (self._max_chip_y + 1)
                else:
                    x = eth_x + chip_x
                    y = eth_y + chip_y
                if (self.is_chip_at(x, y)):
                    yield x, y

    @property
    def maximum_user_cores_on_chip(self):
        """ The maximum number of user cores on any chip
        """
        return self._maximum_user_cores_on_chip

    @property
    def total_available_user_cores(self):
        """ The total number of cores on the machine which are not \
            monitor cores

        :return: total
        :rtype: int
        """
        return sum([chip._n_user_processors for chip in self.chips])

    @property
    def total_cores(self):
        """ The total number of cores on the machine, including monitors

        :return: total
        :rtype: int
        """
        return len([
            processor for chip in self.chips for processor in chip.processors])

    @property
    def has_wrap_arounds(self):
        """ If the machine has wrap around links

        :return: True if wrap around links exist, false otherwise
        :rtype: bool
        """
        return ((self.max_chip_x + 1 == 2 and self.max_chip_y+1 == 2) or
                ((self.max_chip_x + 1) % 12 == 0 and
                 (self.max_chip_y + 1) % 12 == 0))

    def remove_unreachable_chips(self):
        """ Remove chips that can't be reached or that can't reach other chips\
            due to missing links
        """
        for (x, y) in self._unreachable_incoming_chips:
            if (x, y) in self._chips:
                del self._chips[x, y]
        for (x, y) in self._unreachable_outgoing_chips:
            if (x, y) in self._chips:
                del self._chips[x, y]

    @property
    def _unreachable_outgoing_chips(self):
        removable_coords = list()
        for (x, y) in self.chip_coordinates:
            # If no links out of the chip work, remove it
            is_link = False
            for link in range(6):
                if self.is_link_at(x, y, link):
                    is_link = True
                    break
            if not is_link:
                removable_coords.append((x, y))
        return removable_coords

    @property
    def _unreachable_incoming_chips(self):
        removable_coords = list()
        for (x, y) in self.chip_coordinates:
            # Go through all the chips that surround this one
            moves = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]
            is_link = False
            for link, (x_move, y_move) in enumerate(moves):
                opposite = (link + 3) % 6
                next_x = x + x_move
                next_y = y + y_move
                if self.is_link_at(next_x, next_y, opposite):
                    is_link = True
                    break
            if not is_link:
                removable_coords.append((x, y))
        return removable_coords

    @property
    def virtual_chips(self):
        return itervalues(self._virtual_chips)
