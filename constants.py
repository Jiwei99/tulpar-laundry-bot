# Keys
from enum import Enum

STATUS = "status"
USER_USERNAME = "user_username"
USER_ID = "user_id"
START_TIME = "start_time"

CYCLE_TIME = 30

# Encoders
class Encoders(Enum):
    CONFIRM_ENCODER = "+"
    PING_ENCODER = "~"
    DONE_ENCODER = "-"
    CLEAR_ENCODER = "="

# Machines
class Machines(Enum):
    DRYER_1 = "dryer_1"
    DRYER_2 = "dryer_2"
    WASHER_1 = "washer_1"
    WASHER_2 = "washer_2"

    @classmethod
    def get_values(cls):
        return list(map(lambda machine: machine.value, cls))


# Statuses
class Status(Enum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    DONE = "DONE"
