from .machine import Machine


class HorizontalWrapMachine(Machine):
    def __init__(self, width, height, chips, boot_x, boot_y):
        super(HorizontalWrapMachine, self).__init__(width, height, chips, boot_x, boot_y)
