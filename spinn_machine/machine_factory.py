from spinn_machine.no_wrap_machine import NoWrapMachine
from spinn_machine.horizontal_wrap_machine import HorizontalWrapMachine
from spinn_machine.vertical_wrap_machine import VerticalWrapMachine
from spinn_machine.full_wrap_machine import FullWrapMachine
from spinn_machine.router import Router
from spinn_machine.machine import Machine
from spinn_machine.virtual_machine import virtual_machine


def machine_from_size(width, height, chips=None, origin=None):
    """
    Create a machine with the assumed wrap around based on the sizes.

    This could include a machine with no wrap arounds, only vertical ones,
    only horizontal ones or both.

    Note: If the sizes do not match the ones for a known wrap arround machine,
    no wrap arounds is assumed.

    :param width: The width of the machine excluding any vertical chips
    :param height: The height of the machine excluding any vertical chips
    :param chips: Any chips to be add.
    :param origin: Extra inforamation about how this mnachine was created
        to be used in the str method. Example "Virtual" or "Json"
    :return: A sub class of Machine
    """
    if chips is None:
        chips = []
    if width == 2 and height == 2:
        return FullWrapMachine(width, height, chips, origin)
    if width % 12 == 0:
        if height % 12 == 0:
            return FullWrapMachine(width, height, chips, origin)
        else:
            return HorizontalWrapMachine(width, height, chips, origin)
    else:
        if height % 12 == 0:
            return VerticalWrapMachine(width, height, chips, origin)
        else:
            return NoWrapMachine(width, height, chips, origin)


def machine_from_chips(chips):
    """
    Create a machine with the assumed wrap arround based on the sizes.

    The size of the machine is calculated from the list of chips.

    :param chips: Full list of all chips on this machine.
    Or at least a list which includes a chip with the highest x and
    one with the highest Y (excluding any virtual chips)
    :return: A sub class of Machine
    """
    max_x = 0
    max_y = 0
    for chip in chips:
        if chip.x > max_x:
            max_x = chip.x
        if chip.y > max_y:
            max_y = chip.y
    return machine_from_size(max_x + 1, max_y + 1, chips)


def create_one_board_machine(board_version, machine, ethernet_chip):
    """ Creates a virtual machine based off a real machine but just with the \
        system resources of a single board (identified by its ethernet chip).

    :param board_version: The version of board. May be None.
    :param machine: The machine to create the virtual machine from.
    :param ethernet_chip: The chip that can talk to the board's ethernet.
    """
    # build fake setup for the routing
    eth_x = ethernet_chip.x
    eth_y = ethernet_chip.y
    down_links = set()
    fake_machine = machine

    for chip_xy in machine.get_chips_by_ethernet(eth_x, eth_y):
        chip = machine.get_chip_at(*chip_xy)
        # adjust for wrap around's
        fake_x, fake_y = machine.get_local_xy(chip)

        # remove links to ensure it maps on just chips of this board.
        down_links.update({
            (fake_x, fake_y, link)
            for link in range(Router.MAX_LINKS_PER_ROUTER)
            if not chip.router.is_link(link)})

    # Create a fake machine consisting of only the one board that
    # the routes should go over
    if (board_version is None or
            board_version in Machine.BOARD_VERSION_FOR_48_CHIPS) and (
            machine.max_chip_x > Machine.MAX_CHIP_X_ID_ON_ONE_BOARD or
            machine.max_chip_y > Machine.MAX_CHIP_Y_ID_ON_ONE_BOARD):
        down_chips = {
            (x, y) for x, y in Machine.BOARD_48_CHIPS
            if not machine.is_chip_at(
                *machine.get_global_xy(x, y, eth_x, eth_y))}
        # build a fake machine which is just one board but with the
        # missing bits of the real board
        fake_machine = virtual_machine(
            Machine.SIZE_X_OF_ONE_BOARD, Machine.SIZE_Y_OF_ONE_BOARD,
            False, down_chips=down_chips, down_links=down_links)
    return fake_machine
