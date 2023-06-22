from constants import Machines, Encoders
from exceptions import InvalidMachineError

def get_display_label(text: str) -> str:
    return text.capitalize().replace('_', ' ')

def assert_valid_machine(machine: str) -> Machines:
    try:
        return Machines(machine)
    except ValueError:
        raise InvalidMachineError(machine)
    
def is_machine(machine: str) -> bool:
    try:
        assert_valid_machine(machine)
        return True
    except InvalidMachineError:
        return False
    
def encode_machine(machine: str, encoder: Encoders) -> str:
    return f"{encoder.value}{machine}"

def decode_machine(encoded_machine: str, encoder: Encoders) -> str:
    return encoded_machine.strip(encoder.value)