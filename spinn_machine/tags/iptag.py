from spinn_machine.tags.abstract_tag import AbstractTag


class IPTag(AbstractTag):
    """ Used to hold data that is contained within an IPTag
    """

    def __init__(self, board_address, tag, ip_address, port, strip_sdp=False):
        """
        :param board_address: The ip address of the board on which the tag
            is allocated
        :type board_address: str
        :param tag: The tag of the SDP packet
        :type tag: int
        :param ip_address: The IP address to which SDP packets with the tag\
                    will be sent
        :type ip_address: str
        :param port: The port to which the SDP packets with the tag will be\
                    sent
        :type port: int
        :param strip_sdp: Indicates whether the SDP header should be removed
        :type strip_sdp: bool
        :raise None: No known exceptions are raised
        """
        AbstractTag.__init__(self, board_address, tag, port)
        self._ip_address = ip_address
        self._strip_sdp = strip_sdp

    @property
    def ip_address(self):
        """ Return the IP address of the tag
        """
        return self._ip_address

    @property
    def strip_sdp(self):
        """ Return if the sdp header is to be stripped
        """
        return self._strip_sdp

    def __str__(self):
        return "IP Tag on {}: tag={} port={} ip_address={}".format(
            self._board_address, self._tag, self._port, self._ip_address)
