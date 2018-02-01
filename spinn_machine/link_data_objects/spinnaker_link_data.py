from .abstract_link_data import AbstractLinkData


class SpinnakerLinkData(AbstractLinkData):
    """ Data object for spinnaker links
    """

    __slots__ = [
        "_spinnaker_link_id"]

    # pylint: disable=too-many-arguments
    def __init__(self, spinnaker_link_id, connected_chip_x, connected_chip_y,
                 connected_link, board_address):
        super(SpinnakerLinkData, self).__init__(
            connected_chip_x, connected_chip_y, connected_link, board_address)
        self._spinnaker_link_id = spinnaker_link_id

    @property
    def spinnaker_link_id(self):
        """ The ID of the spinnaker link.
        """
        return self._spinnaker_link_id
