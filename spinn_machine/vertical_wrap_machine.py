from .machine import Machine


class VerticalWrapMachine(Machine):
    def __init__(self, width, height, chips, boot_x, boot_y):
        super(VerticalWrapMachine, self).__init__(width, height, chips, boot_x, boot_y)
