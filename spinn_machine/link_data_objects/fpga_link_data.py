from spinn_machine.link_data_objects.abstract_link_data import AbstractLinkData


class FPGALinkData(AbstractLinkData):
    """ Data object for FPGA links
    """

    __slots__ = (
        "_fpga_link_id",
        "_fpga_id"
    )

    def __init__(self, fpga_link_id, fpga_id, connected_chip_x,
                 connected_chip_y, connected_link, board_address):
        AbstractLinkData.__init__(
            self, connected_chip_x, connected_chip_y, connected_link,
            board_address)
        self._fpga_link_id = fpga_link_id
        self._fpga_id = fpga_id

    @property
    def fpga_link_id(self):
        return self._fpga_link_id

    @property
    def fpga_id(self):
        return self._fpga_id
