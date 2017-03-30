class AbstractLinkData(object):
    """ Data object for spinnaker links
    """

    __slots__ = (
        "_board_address",
        "_connected_chip_x",
        "_connected_chip_y",
        "_connected_link"
    )

    def __init__(self, connected_chip_x, connected_chip_y, connected_link,
                 board_address):
        self._board_address = board_address
        self._connected_chip_x = connected_chip_x
        self._connected_chip_y = connected_chip_y
        self._connected_link = connected_link

    @property
    def board_address(self):
        """
        property method for board address
        """
        return self._board_address

    @property
    def connected_chip_x(self):
        """
        property method for connected chip x
        """
        return self._connected_chip_x

    @property
    def connected_chip_y(self):
        """
        property method for connected chip y
        """
        return self._connected_chip_y

    @property
    def connected_link(self):
        """
        property for connected link
        """
        return self._connected_link
