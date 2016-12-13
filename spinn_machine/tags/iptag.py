from spinn_machine.tags.abstract_tag import AbstractTag


class IPTag(AbstractTag):
    """ Used to hold data that is contained within an IPTag
    """

    def __init__(
            self, board_address, tag, ip_address, port=None,
            strip_sdp=False, traffic_identifier="DEFAULT"):
        """
        :param board_address: The ip address of the board on which the tag
            is allocated
        :type board_address: str or None
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
        :param traffic_identifier: the human readable identifier for traffic
        transmitted using this tag
        :type traffic_identifier: str
        :raise None: No known exceptions are raised
        """
        AbstractTag.__init__(self, board_address, tag, port)
        self._ip_address = ip_address
        self._strip_sdp = strip_sdp
        self._traffic_identifier = traffic_identifier

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
        """ An human readable identifier for what type of traffic is to go
        through this tag
        """
        return self._traffic_identifier

    def __repr__(self):
        return (
            "IPTag(board_address={}, tag={}, port={}, ip_address={},"
            " strip_sdp={}, traffic_identifier={})".format(
                self._board_address, self._tag, self._port, self._ip_address,
                self._strip_sdp, self._traffic_identifier))

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
