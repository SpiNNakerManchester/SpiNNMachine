from .machine import Machine


class HorizontalWrapMachine(Machine):
    def __init__(self, chips, boot_x, boot_y):
        super(HorizontalWrapMachine, self).__init__(chips, boot_x, boot_y)
