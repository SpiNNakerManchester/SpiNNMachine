"""
SpinnakerLinkData
"""


class SpinnakerLinkData(object):
    """ Data object for spinnaker links
    """

    def __init__(self, spinnaker_link_id, connected_chip_x, connected_chip_y,
                 connected_link):
        self._spinnaker_link_id = spinnaker_link_id
        self._connected_chip_x = connected_chip_x
        self._connected_chip_y = connected_chip_y
        self._connected_link = connected_link

    @property
    def spinnaker_link_id(self):
        """ Get the id of the spinnaker link
        """
        return self._spinnaker_link_id

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
