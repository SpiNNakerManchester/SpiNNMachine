from spinn_machine.tags.abstract_tag import AbstractTag


class IPTag(AbstractTag):
    """ Used to hold data that is contained within an IPTag
    """

    def __init__(
            self, board_address, destination_x, destination_y, tag, ip_address,
            port=None, strip_sdp=False, traffic_identifier="DEFAULT"):
        """
        :param board_address: The ip address of the board on which the tag\
            is allocated
        :type board_address: str or None
        :param destination_x: The x-coordinate where users of this tag should\
            send packets to
        :type destination_x: int
        :param destination_y: The y-coordinate where users of this tag should\
            send packets to
        :type destination_y: int
        :param tag: The tag of the SDP packet
        :type tag: int
        :param ip_address: The IP address to which SDP packets with the tag\
                    will be sent
        :type ip_address: str
        :param port: The port to which the SDP packets with the tag will be\
                    sent
        :type port: int or None if not yet assigned
        :param strip_sdp: Indicates whether the SDP header should be removed
        :type strip_sdp: bool
        :param traffic_identifier: the identifier for traffic transmitted\
             using this tag
        :type traffic_identifier: str
        :raise None: No known exceptions are raised
        """
        AbstractTag.__init__(self, board_address, tag, port)
        self._ip_address = ip_address
        self._strip_sdp = strip_sdp
        self._traffic_identifier = traffic_identifier
        self._destination_x = destination_x
        self._destination_y = destination_y

    @property
    def ip_address(self):
        """ Return the IP address of the tag
        """
        return self._ip_address

    @property
    def strip_sdp(self):
        """ Return if the SDP header is to be stripped
        """
        return self._strip_sdp

    @property
    def traffic_identifier(self):
        """ The identifier of traffic using this tag
        """
        return self._traffic_identifier

    @property
    def destination_x(self):
        """ The x-coordinate where users of this tag should send packets to
        """
        return self._destination_x

    @property
    def destination_y(self):
        """ The y-coordinate where users of this tag should send packets to
        """
        return self._destination_y

    def __repr__(self):
        return (
            "IPTag(board_address={}, destination_x={}, destination_y={},"
            " tag={}, port={}, ip_address={}, strip_sdp={},"
            " traffic_identifier={})".format(
                self._board_address, self._destination_x, self._destination_y,
                self._tag, self._port, self._ip_address, self._strip_sdp,
                self._traffic_identifier))

    def __eq__(self, other):
        if not isinstance(other, IPTag):
            return False
        else:
            if (self._ip_address == other._ip_address and
                    self._strip_sdp == other._strip_sdp and
                    self._board_address == other.board_address and
                    self._port == other.port and
                    self._tag == other.tag and
                    self._traffic_identifier == other.traffic_identifier):
                return True
            else:
                return False

    def __hash__(self):
        return hash((self._ip_address, self._strip_sdp, self._board_address,
                     self._port, self._tag, self._traffic_identifier))

    def __ne__(self, other):
        return not self.__eq__(other)
