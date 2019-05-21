from .machine import Machine


class VerticalWrapMachine(Machine):
    def __init__(self, chips, boot_x, boot_y):
        super(VerticalWrapMachine, self).__init__(chips, boot_x, boot_y)
