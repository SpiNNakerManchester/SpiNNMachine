from .machine import Machine


class FullWrapMachine(Machine):
    def __init__(self, chips, boot_x, boot_y):
        super(FullWrapMachine, self).__init__(chips, boot_x, boot_y)
