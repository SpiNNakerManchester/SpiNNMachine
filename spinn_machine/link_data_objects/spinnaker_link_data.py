from .abstract_link_data import AbstractLinkData


class SpinnakerLinkData(AbstractLinkData):
    """ Data object for SpiNNaker links
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

    def __eq__(self, other):
        if not isinstance(other, SpinnakerLinkData):
            return False
        return (self._spinnaker_link_id == other.spinnaker_link_id and
                self.connected_chip_x == other.connected_chip_x and
                self.connected_chip_y == other.connected_chip_y and
                self.connected_link == other.connected_link and
                self.board_address == other.board_address)

    def __hash__(self):
        return hash((self._spinnaker_link_id,
                     self.connected_chip_x, self.connected_chip_y,
                     self.connected_link, self.board_address))
