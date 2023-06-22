class InvalidMachineError(Exception):
    def __init__(self, machine):
        self.message = f"{machine} is not a valid machine"
        super().__init__(self.message)
