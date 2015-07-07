"""
SpinnakerLinkData
"""


class SpinnakerLinkData(object):
    """
    data object for spinnaker links
    """

    def __init__(self, connected_chip_x, connected_chip_y, connected_link):
        self._connected_chip_x = connected_chip_x
        self._connected_chip_y = connected_chip_y
        self._connected_link = connected_link

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
