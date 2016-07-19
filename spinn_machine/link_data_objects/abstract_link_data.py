"""
AbstractLinkData
"""
from six import add_metaclass
from abc import ABCMeta


@add_metaclass(ABCMeta)
class AbstractLinkData(object):
    """ Data object for spinnaker links
    """

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
        :return:
        """
        return self._board_address

    @property
    def connected_chip_x(self):
        """
        property method for connected chip x
        :return:
        """
        return self._connected_chip_x

    @property
    def connected_chip_y(self):
        """
        property method for connected chip y
        :return:
        """
        return self._connected_chip_y

    @property
    def connected_link(self):
        """
        property for connected link
        :return:
        """
        return self._connected_link
