from spinn_machine.link_data_objects.abstract_link_data import AbstractLinkData


class SpinnakerLinkData(AbstractLinkData):
    """ Data object for spinnaker links
    """

    __slots__ = (
        "_spinnaker_link_id"
    )

    def __init__(self, spinnaker_link_id, connected_chip_x, connected_chip_y,
                 connected_link, board_address):
        AbstractLinkData.__init__(
            self, connected_chip_x, connected_chip_y, connected_link,
            board_address)
        self._spinnaker_link_id = spinnaker_link_id

    @property
    def spinnaker_link_id(self):
        """ Get the id of the spinnaker link
        """
        return self._spinnaker_link_id
