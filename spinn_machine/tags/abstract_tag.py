class AbstractTag(object):
    """ Common properties of SpiNNaker IP tags and reverse IP tags.
    """

    __slots__ = [
        # the board address associated with this tag
        "_board_address",

        # the tag id associated with this tag
        "_tag",

        # the port number associated with this tag
        "_port"
    ]

    def __init__(self, board_address, tag, port):
        self._board_address = board_address
        self._tag = tag
        self._port = port

    @property
    def board_address(self):
        """ The board address of the tag
        """
        return self._board_address

    @property
    def tag(self):
        """ The tag ID of the tag
        """
        return self._tag

    @property
    def port(self):
        """ The port of the tag
        """
        return self._port

    @port.setter
    def port(self, port):
        """ Set the port; will fail if the port is already set
        """
        if self._port is not None:
            raise RuntimeError("Port cannot be set more than once")
        self._port = port
