
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
            raise exceptions.SpinnMachineAlreadyExistsException(
                "chip", "{}, {}".format(chip.x, chip.y))

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
        if spinnaker_link.board_address in self._spinnaker_links:
            links = self._spinnaker_links[spinnaker_link.board_address]
            if spinnaker_link.spinnaker_link_id in links:
                raise exceptions.SpinnMachineAlreadyExistsException(
                    "spinnaker_link", spinnaker_link.spinnaker_link_id)
        else:
            self._spinnaker_links[spinnaker_link.board_address] = dict()

        self._spinnaker_links[spinnaker_link.board_address][
            spinnaker_link.spinnaker_link_id] = spinnaker_link

    @property
    def spinnaker_links(self):
        """ The set of spinnaker links in the machine

        :return: An iterable of spinnaker links
        :rtype: iterable of\
            :py:class:`spinn_machine.spinnaker_link_data.SpinnakerLinkData`
        """
        return self._spinnaker_links.iteritems()

    def get_spinnaker_link_with_id(self, spinnaker_link_id, board_address):
        """ Get a spinnaker link with a given id

        :param spinnaker_link_id: The id of the link
        :type spinnaker_link_id: int
        :param board_address:\
            the board address that this spinnaker link is associated with
        :type board_address: str
        :rtype:\
            :py:class:`spinn_machine.link_data_objects.spinnaker_link_data.SpinnakerLinkData`
        """
        return self._spinnaker_links[board_address][spinnaker_link_id]

    def get_fpga_link_with_id(self, board_address, fpga_link_id, fpga_id):
        """ Get an FPGA link data item that corresponds to the FPGA and FPGA\
            link for a given board address.
        :param board_address:\
            the board address that this spinnaker link is associated with
        :type board_address: str
        :param fpga_link_id:\
            the link id of the FPGA. Refer to technical document\
            spinn4-5.pdf located here for more detail:
            https://drive.google.com/drive/folders/0B9312BuJXntlb2w0OGx1OVU5cmc
        :type fpga_id: int
        :param fpga_id:\
            the id of the FPGA that the data is going through.  Refer to \
            technical document spinn4-5.pdf located here for more detail:
            https://drive.google.com/drive/folders/0B9312BuJXntlb2w0OGx1OVU5cmc
        :type fpga_link_id: int
        :rtype:\
            :py:class:`spinn_machine.link_data_objects.fpga_link_data.FPGALinkData`
        :return: the given FPGA link object
        """
        for ethernet_connected_chip in self._ethernet_connected_chips:
            if ethernet_connected_chip.ip_address == board_address:
                chip, link_id = self._locate_fpga_link_real_chip(
                    fpga_link_id, fpga_id, ethernet_connected_chip)
                if chip is None:
                    raise exceptions.SpinnMachineInvalidParameterException(
                        "fpga_link_id, fpga_id, board_address",
                        "None",
                        "The FPGA link is attempting to connect to a chip that"
                        " does not exist in this machine.")
                return FPGALinkData(fpga_link_id, fpga_id, chip.x, chip.y,
                                    link_id, board_address)
        return None

    def _locate_fpga_link_real_chip(
            self, fpga_link_id, fpga_id, ethernet_connected_chip):
        """

        :param fpga_link_id:\
            the link id of the FPGA. Refer to technical document\
            spinn4-5.pdf located here for more detail:
            https://drive.google.com/drive/folders/0B9312BuJXntlb2w0OGx1OVU5cmc
        :type fpga_id: int
        :param fpga_id:\
            the id of the FPGA that the data is going through.  Refer to \
            technical document spinn4-5.pdf located here for more detail:
            https://drive.google.com/drive/folders/0B9312BuJXntlb2w0OGx1OVU5cmc
        :type fpga_link_id: int
        :param ethernet_connected_chip:\
            chip that is the root of the board that this FPGA is connected
        :type ethernet_connected_chip: `:py:class:`spinn_machine.chip.Chip`
        :return: (chip, link_id) data on which real chip the FPGA link goes to
        :rtype: (:py:class:`spinn_machine.chip.Chip`, int)
        """

        chips_to_fpga = {0: [], 1: [], 2: []}

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
        chips = {'left': [], 'left_north': [], 'north': [], 'right': [],
                 'right_south': [], 'south': []}

        # handle the first chip
        chip = ethernet_connected_chip
        chips['left'].append(chip)
        x = ethernet_connected_chip.x
        y = ethernet_connected_chip.y

        # handle left chips (goes up 4)
        for _ in range(0, 3):
            y = (y + 1) % (self._max_chip_y + 1)
            print "A"
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

        # map chips to which FPGA and FPGA link will be used
        # (array index = fpga_link_id)

        # handle left
        for chip in chips['left']:
            chips_to_fpga[1].append((chip, 4))
            chips_to_fpga[1].append((chip, 3))

        # handle left north
        first = chips['left_north'][0]
        last = chips['left_north'][-1]
        for chip in chips['left_north']:
            if chip == first:
                chips_to_fpga[1].append((chip, 2))
            elif chip == last:
                chips_to_fpga[1].append((chip, 3))
            else:
                chips_to_fpga[1].append((chip, 3))
                chips_to_fpga[1].append((chip, 2))

        # handle north
        for chip in chips['north']:
            chips_to_fpga[2].append((chip, 2))
            chips_to_fpga[2].append((chip, 1))

        # handle right
        first = chips['right'][0]
        last = chips['right'][-1]
        for chip in chips['right']:
            if chip == first:
                chips_to_fpga[2].append((chip, 0))
            elif chip == last:
                chips_to_fpga[2].append((chip, 1))
            else:
                chips_to_fpga[2].append((chip, 1))
                chips_to_fpga[2].append((chip, 0))

        # handle right south
        for chip in chips['right_south']:
            chips_to_fpga[0].append((chip, 0))
            chips_to_fpga[0].append((chip, 5))

        # handle south
        first = chips['south'][0]
        last = chips['south'][-1]
        for chip in chips['south']:
            if chip == first:
                chips_to_fpga[0].append((chip, 4))
            elif chip == last:
                chips_to_fpga[0].append((chip, 5))
            else:
                chips_to_fpga[0].append((chip, 5))
                chips_to_fpga[0].append((chip, 4))

        # get FPGA link from the arrays
        return chips_to_fpga[fpga_id][fpga_link_id]

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

    def locate_spinnaker_links(self, version_no, machine):
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
                spinnaker_links.append(SpinnakerLinkData(
                    0, 0, 0, 3, chip.ip_address))
            chip = self.get_chip_at(1, 0)
            if not chip.router.is_link(0):
                spinnaker_links.append(SpinnakerLinkData(
                    1, 1, 0, 0, chip.ip_address))
        elif version_no == 4 or version_no == 5:
            for ethernet_connected_chip in machine.ethernet_connected_chips:
                if not ethernet_connected_chip.router.is_link(4):
                    spinnaker_links.append(SpinnakerLinkData(
                        0, 0, 0, 4, ethernet_connected_chip.ip_address))
        elif version_no is None:

            # multi-board virtual machine
            for ethernet_connected_chip in machine.ethernet_connected_chips:
                if not ethernet_connected_chip.router.is_link(4):
                    spinnaker_links.append(SpinnakerLinkData(
                        0, 0, 0, 4, ethernet_connected_chip.ip_address))
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
