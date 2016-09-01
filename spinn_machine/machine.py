
# spinn_machine imports
from spinn_machine import exceptions
from spinn_machine.link_data_objects.fpga_link_data import FPGALinkData
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

    __slots__ = (
        "_boot_x",
        "_boot_y",
        "_boot_ethernet_address",
        "_chips",
        "_chips_by_local_ethernet",
        "_ethernet_connected_chips",
        "_fpga_links",
        "_max_chip_x",
        "_max_chip_y",
        "_spinnaker_links"
    )

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

        chip_id = (chip.nearest_ethernet_x, chip.nearest_ethernet_y)
        if chip_id not in self._chips_by_local_ethernet:
            self._chips_by_local_ethernet[chip_id] = list()
        self._chips_by_local_ethernet[chip_id].append(chip)

    def get_chips_via_local_ethernet(self, local_ethernet_x, local_ethernet_y):
        """ Get a list of chips which have the nearest Ethernet chip of x and y
        :param local_ethernet_x: the Ethernet chip x coord
        :param local_ethernet_y: the Ethernet chip y coord
        :return: list of chips
        """
        return self._chips_by_local_ethernet.get(
            (local_ethernet_x, local_ethernet_y), [])

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
            chip = self.get_chip_at(0, 0)
            if not chip.router.is_link(3):
                self._spinnaker_links[chip.ip_address, 0] = SpinnakerLinkData(
                    0, 0, 0, 3, chip.ip_address)
            chip = self.get_chip_at(1, 0)
            if not chip.router.is_link(0):
                self._spinnaker_links[chip.ip_address, 1] = SpinnakerLinkData(
                    1, 1, 0, 0, chip.ip_address)
        elif version_no == 4 or version_no == 5 or version_no is None:
            for chip in self._ethernet_connected_chips:
                if not chip.router.is_link(4):
                    self._spinnaker_links[
                        chip.ip_address, 0] = SpinnakerLinkData(
                            0, 0, 0, 4, chip.ip_address)

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
                chip = ethernet_connected_chip
                x = ethernet_connected_chip.x
                y = ethernet_connected_chip.y
                ip = ethernet_connected_chip.ip_address

                # handle left chips (goes up 4)
                chips['left'].append(chip)
                for _ in range(0, 3):
                    y = (y + 1) % (self._max_chip_y + 1)
                    chip = self.get_chip_at(x, y)
                    chips['left'].append(chip)

                # handle left north (goes across 4 but add this chip)
                chips['left_north'].append(chip)
                for _ in range(0, 4):
                    x = (x + 1) % (self._max_chip_x + 1)
                    y = (y + 1) % (self._max_chip_y + 1)
                    chip = self.get_chip_at(x, y)
                    chips['left_north'].append(chip)

                # handle north (goes left 3 but add this chip)
                chips['north'].append(chip)
                for _ in range(0, 3):
                    x = (x + 1) % (self._max_chip_x + 1)
                    chip = self.get_chip_at(x, y)
                    chips['north'].append(chip)

                # handle east (goes down 4 but add this chip)
                chips['right'].append(chip)
                for _ in range(0, 4):
                    y = (y - 1) % (self._max_chip_y + 1)
                    chip = self.get_chip_at(x, y)
                    chips['right'].append(chip)

                # handle east south (goes down across 3 but add this chip)
                chips['right_south'].append(chip)
                for _ in range(0, 3):
                    x = (x - 1) % (self._max_chip_x + 1)
                    y = (y - 1) % (self._max_chip_y + 1)
                    chip = self.get_chip_at(x, y)
                    chips['right_south'].append(chip)

                # handle south (goes across 3 but add this chip)
                chips['south'].append(chip)
                for _ in range(0, 4):
                    x = (x - 1) % (self._max_chip_x + 1)
                    chip = self.get_chip_at(x, y)
                    chips['south'].append(chip)

                # handle left
                fpga_id = 1
                fpga_link = 0
                for chip in chips['left']:
                    self._add_fpga_link(fpga_id, fpga_link, chip, 4, ip)
                    fpga_link += 1
                    self._add_fpga_link(fpga_id, fpga_link, chip, 3, ip)
                    fpga_link += 1

                # handle left north
                first = chips['left_north'][0]
                last = chips['left_north'][-1]
                for chip in chips['left_north']:
                    if chip == first:
                        self._add_fpga_link(fpga_id, fpga_link, chip, 2, ip)
                        fpga_link += 1
                    elif chip == last:
                        self._add_fpga_link(fpga_id, fpga_link, chip, 3, ip)
                        fpga_link += 1
                    else:
                        self._add_fpga_link(fpga_id, fpga_link, chip, 3, ip)
                        fpga_link += 1
                        self._add_fpga_link(fpga_id, fpga_link, chip, 2, ip)
                        fpga_link += 1

                # handle north
                fpga_id = 2
                fpga_link = 0
                for chip in chips['north']:
                    self._add_fpga_link(fpga_id, fpga_link, chip, 2, ip)
                    fpga_link += 1
                    self._add_fpga_link(fpga_id, fpga_link, chip, 1, ip)
                    fpga_link += 1

                # handle right
                first = chips['right'][0]
                last = chips['right'][-1]
                for chip in chips['right']:
                    if chip == first:
                        self._add_fpga_link(fpga_id, fpga_link, chip, 0, ip)
                        fpga_link += 1
                    elif chip == last:
                        self._add_fpga_link(fpga_id, fpga_link, chip, 1, ip)
                        fpga_link += 1
                    else:
                        self._add_fpga_link(fpga_id, fpga_link, chip, 1, ip)
                        fpga_link += 1
                        self._add_fpga_link(fpga_id, fpga_link, chip, 0, ip)
                        fpga_link += 1

                # handle right south
                fpga_id = 0
                fpga_link = 0
                for chip in chips['right_south']:
                    self._add_fpga_link(fpga_id, fpga_link, chip, 0, ip)
                    fpga_link += 1
                    self._add_fpga_link(fpga_id, fpga_link, chip, 5, ip)
                    fpga_link += 1

                # handle south
                first = chips['south'][0]
                last = chips['south'][-1]
                for chip in chips['south']:
                    if chip == first:
                        self._add_fpga_link(fpga_id, fpga_link, chip, 4, ip)
                        fpga_link += 1
                    elif chip == last:
                        self._add_fpga_link(fpga_id, fpga_link, chip, 5, ip)
                        fpga_link += 1
                    else:
                        self._add_fpga_link(fpga_id, fpga_link, chip, 5, ip)
                        fpga_link += 1
                        self._add_fpga_link(fpga_id, fpga_link, chip, 4, ip)
                        fpga_link += 1

    def _add_fpga_link(self, fpga_id, fpga_link, chip, link, board_address):
        if chip is not None:
            if not chip.router.is_link(link):
                self._fpga_links[board_address, fpga_id, fpga_link] = \
                    FPGALinkData(
                        fpga_link_id=fpga_link, fpga_id=fpga_id,
                        connected_chip_x=chip.x, connected_chip_y=chip.y,
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
