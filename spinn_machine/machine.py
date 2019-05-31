try:
    from collections.abc import OrderedDict
except ImportError:
    from collections import OrderedDict
from six import iteritems, iterkeys, itervalues, add_metaclass
from .exceptions import (SpinnMachineAlreadyExistsException,
                         SpinnMachineException)
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
        "_boot_ethernet_address",
        # List of the possible chips (x,y) on each board of the machine
        "_board_chips",
        "_chips",
        "_ethernet_connected_chips",
        "_fpga_links",
        # Declared height of the machine excluding virtual chips
        # This can not be changed
        "_height",
        # Max x value of any chip including virtual chips
        # This could change as new chips are added
        "_max_chip_x",
        # Max y value of any chip including virtual chips
        # This could change as new chips are added
        "_max_chip_y",
        # Extra inforamtion about how this mnachine was created
        # to be used in the str method
        "_origin",
        "_spinnaker_links",
        "_maximum_user_cores_on_chip",
        "_virtual_chips",
        # Declared width of the machine excluding virtual chips
        # This can not be changed
        "_width"
    )

    def __init__(self, width, height, chips=None, origin=None):
        """
        Creates an abstarct machine that must be superclassed by wrap type.

        Use machine_fatcory methods to dettermine the correct machine class

        :param width: The width of the machine excluding any virtual chips
        :param height: The height of the machine excluding any virtual chips
        :param chips: An iterable of chips in the machine
        :type chips: iterable of :py:class:`~spinn_machine.Chip`
        :param origin: Extra inforamation about how this mnachine was created
        to be used in the str method. Example "Virtual" or "Json"
        :raise spinn_machine.exceptions.SpinnMachineAlreadyExistsException: \
            If any two chips have the same x and y coordinates
        """
        self._width = width
        self._height = height

        if (self._width == self._height == 8) or \
                self.multiple_48_chip_boards():
            self._board_chips = self.BOARD_48_CHIPS
        else:
            self._board_chips = []
            for x in range(width):
                for y in range(height):
                    self._board_chips.append((x, y))

        # The current maximum chip x coordinate
        self._max_chip_x = 0

        # The current maximum chip y coordinate
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
        self._boot_ethernet_address = None

        # The dictionary of chips
        self._chips = OrderedDict()
        if chips is not None:
            self.add_chips(chips)

        self._virtual_chips = list()

        if origin is None:
            self._origin = ""
        else:
            self._origin = origin

    @abstractmethod
    def multiple_48_chip_boards(self):
        """
        Checks that the width and height coorespond to the expected size for a
        multi board machine made up of more than one 48 chip board.

        The assumption is that any size machine can be supported but that
        only ones with an expected 48 chip board size can have more than one
        ethernet chip.

        +++++
        return: True if this machine can have multiple 48 chip boards
        """

    @abstractmethod
    def get_xys_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yields the protential x,y locations of all the chips on the board
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
    def get_chips_by_ethernet(self, ethernet_x, ethernet_y):
        """
        Yeilds the actual chips on the board with this ethernet.
        Including the Ethernet chip itself.

        Wraparounds are handled as appropriate.

        This method does check if the chip actually exists.

        :param ethernet_x: The x coordinate of a (local 0,0) legal ethernet
        chip
        :param ethernet_y: The x coordinate of a (local 0,0) legal ethernet
        chip
        :return: Yeilds the chips on (x, Y) chips on this board.
        """

    @abstractmethod
    def xy_over_link(self, x, y, link):
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
        generates x,y values that fall outside of the legal values including
        negative values, x = width or y = height.

        :param x: The x coordinate of a chip that will exist on the machine
        :param y: The x coordinate of a chip that will exist on the machine
        :param link: The link to another chip that could exist on the machine
        :return: x and y coordinates of the chip over that link if it is valid
        or some fictional x y if not.
        """

    @abstractmethod
    def get_local_xy(self, chip):
        """
        Converts the x and y cooridinates into the local cooridnates on the
        board as if the ethernet was at position 0,0

        This method does take wrap arounds into consideration.

        This method assumes that chip is on the machine or is a copy of a
        chip on the machine

        :param chip. A Chip in the machine
        :return: Local (x, y) coordinates.
        """

    @abstractmethod
    def get_global_xy(self, local_x, local_y, ethernet_x, ethernet_y):
        """
        Converts the local x and y cooridinates into global x,y coordinates,
        under the assumption that they are on the board with local 0,0 at
        ethernet_x, ethernet_y

        This method does take wrap arounds into consideration.

        GIGO: This method does not check if input parameters make sense,
        nor does it check if there is a chip at the resulting global x,y

        :param chip. A Chip in the machine
        :return: Local (x, y) coordinates.

        :param local_x: A valid local x coorindate for a chip
        :param local_y: A valid local y coorindate for a chip
        :param ethernet_x: The global ethernet x for the board the chip is on
        :param ethernet_y: The global ethernet y for the board the chip is on
        :return: global (x,y) cooridinates of the chip
        """

    def validate(self):
        """
        Validates the machine and raises an exception in unexpected conditions.

        Assumes that at the time this is called all chips are on the board.

        This allows the checks to be avoided when creating a virtual machine
        (Except of course in testing)

        An Error is raised if there is a chip with a x outside of the
        range 0 to width -1 (except for virtual ones)
        An Error is raised if there is a chip with a y outside of the
        range 0 to height -1 (except for virtual ones)
        An Error is raise if there is no chip at the declared ethernet x and y
        An Error is raised if an ethernet chip is not at a local 0,0
        An Error is raised if there is no ethernet chip is at 0,0
        An Error is raised if this is a unexpected multiple board situation

        """
        if self._boot_ethernet_address is None:
            raise SpinnMachineException(
                "no ethernet chip at 0, 0 found")
        if len(self._ethernet_connected_chips) > 1:
            if not self.multiple_48_chip_boards():
                raise SpinnMachineException(
                    "A {} machine of size {}, {} can not handle multiple "
                    "ethernet chips".format(
                        self.wrap, self._width, self._height))
        # The fact that self._boot_ethernet_address is set means there is an
        # ethernet chip and it is at 0,0 so no need to check that

        for chip in self.chips:
            if chip.x < 0:
                raise SpinnMachineException(
                    "{} has a negative x".format(chip))
            if chip.y < 0:
                raise SpinnMachineException(
                    "{} has a negative y".format(chip))
            if not chip.virtual:
                if chip.x >= self._width:
                    raise SpinnMachineException(
                        "{} has an x large than width {}".format(
                            chip, self._width))
                if chip.y >= self._height:
                    raise SpinnMachineException(
                        "{} has an y large than heigth {}".format(
                            chip, self._width))
            if chip.ip_address:
                # Ethernet Chip checks
                if chip.x % 4 != 0:
                    raise SpinnMachineException(
                        "Ethernet {} has a x which is not divisible by 4"
                        "".format(chip))
                if (chip.x + chip.y) % 12 != 0:
                    raise SpinnMachineException(
                        "Ethernet {} has a x y pair that do not add up to 12"
                        "".format(chip))
            elif not chip.virtual:
                # None Ethernet chip checks
                if not self.is_chip_at(
                        chip.nearest_ethernet_x, chip.nearest_ethernet_y):
                    raise SpinnMachineException(
                        "{} has an invalid ethernet chip".format(chip))
                local_xy = self.get_local_xy(chip)
                if local_xy not in self._board_chips:
                    raise SpinnMachineException(
                        "{} has an unexpected local xy of {}".format(
                            chip, local_xy))

    @abstractproperty
    def wrap(self):
        """
        String to represent the type of wrap.
        :return: Short String for type of wrap
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

        self._chips[chip_id] = chip

        if chip.x > self._max_chip_x:
            self._max_chip_x = chip.x
        if chip.y > self._max_chip_y:
            self._max_chip_y = chip.y

        if chip.ip_address is not None:
            self._ethernet_connected_chips.append(chip)
            if (chip.x == 0) and (chip.y == 0):
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
        return "[{}{}Machine: max_x={}, max_y={}, n_chips={}]".format(
            self._origin, self.wrap, self._max_chip_x, self._max_chip_y,
            self.n_chips)

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
    def boot_chip(self):
        """ The chip used to boot the machine

        :rtype: `~py:class:spinn_machine.Chip`
        """
        return self._chips[0, 0]

    def get_chips_on_board(self, chip):
        """ Get the chips that are on the same board as the given chip

        :param chip: The chip to find other chips on the same board as
        :return: An iterable of (x, y) coordinates of chips on the same board
        :rtype: iterable(tuple(int,int))
        """
        return self.get_chips_by_ethernet(
            chip.nearest_ethernet_x, chip.nearest_ethernet_y)

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
