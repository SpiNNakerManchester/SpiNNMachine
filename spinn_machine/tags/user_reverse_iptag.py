from spinn_machine.tags.abstract_user_tag import AbstractUserTag

class UserReverseIPTag(AbstractUserTag):
    """ Used to hold data that is contained within an IPTag
    """

    def __init__(self, ip_address, port, tag=None, sdp_port=1):
        """
        :param ip_address: The ip address of the board on which the tag
            is allocated
        :type ip_address: str
        :param tag: The requested tag for SDP packets originated from this input
        :type tag: int
        :param port: The UDP port on which SpiNNaker will listen for packets
        :type port: int
        :param sdp_port: The optional port number to use for SDP packets that\
                    are formed on the machine (default is 1)
        :type sdp_port: int
        :raise None: No known exceptions are raised
        """
        AbstractUserTag.__init__(self, ip_address, port, tag, ip_address)
        self._sdp_port = sdp_port

    @property
    def sdp_port(self):
        """returns the sdp port of the tag
        :return:
        """
        return self._sdp_port
