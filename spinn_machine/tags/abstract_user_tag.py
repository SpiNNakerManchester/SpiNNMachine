from spinn_machine.tags.abstract_tag import AbstractTag

class AbstractUserTag(AbstractTag):
    """ Used to hold data representing a user-requested tag
    """

    def __init__(self, ip_address, port, tag=None, board=None):
        """
        :param ip_address: The IP address associated with the tag
        :type ip_address: str
        :param port: The port associated with the tag 
        :type port: int
        :param tag: The SDP tag
        :type tag: int
        :raise None: No known exceptions are raised
        """
        AbstractTag.__init__(self, board, tag, port)
        self._ip_address = ip_address

    @property
    def ip_address(self):
        """ The ip address associated with the tag
        """
        return self._ip_address

    @property
    def board(self):
        return self._board_address
