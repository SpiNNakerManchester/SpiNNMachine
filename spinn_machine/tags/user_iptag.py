from spinn_machine.tags.abstract_user_tag import AbstractUserTag


class UserIPTag(AbstractUserTag):
    """ Used to hold data that is contained within an IPTag
    """

    def __init__(self, ip_address, port, tag=None, board=None, strip_sdp=False):
        """
        :param ip_address: The IP address to which SDP packets with the tag\
                    will be sent
        :type ip_address: str
        :param port: The port to which the SDP packets with the tag will be\
                    sent
        :type port: int
        :param tag: The tag of the SDP packet
        :type tag: int
        :param strip_sdp: Indicates whether the SDP header should be removed
        :type strip_sdp: bool
        :raise None: No known exceptions are raised
        """
        AbstractUserTag.__init__(self, ip_address, port, tag, board)
        self._strip_sdp = strip_sdp

    @property
    def strip_sdp(self):
        """ Return if the sdp header is to be stripped
        """
        return self._strip_sdp
