from typing import Dict, List
import db
from datetime import datetime
import math
from pytz import timezone
from exceptions import InvalidMachineError
import utils
from constants import Machines, Status, STATUS, USER_ID, USER_USERNAME, START_TIME, CYCLE_TIME

def get_status() -> str:
    statuses = db.get_status()
    message = ""
    for machine in statuses:
        machine_text = utils.get_display_label(machine)
        user = statuses[machine][USER_USERNAME]
        time = datetime.fromisoformat(statuses[machine][START_TIME]).astimezone(tz=timezone("Asia/Singapore"))

        try:
            status = Status(statuses[machine][STATUS])
            if status == Status.AVAILABLE:
                message += f"<b>{machine_text}:</b> ✅ Available\n"
            elif status == Status.IN_USE:
                time_left = CYCLE_TIME - math.floor((datetime.now() - time).total_seconds() / 60)
                time_left = time_left if time_left > 0 else 0
                mins = "min" if time_left == 1 else "mins"
                message += f"<b>{machine_text}:</b> ❌ In Use ({time_left} {mins} - @{user})\n"
            elif status == Status.DONE:
                time_ended = time + datetime.timedelta(minutes=CYCLE_TIME)
                message += f"<b>{machine_text}:</b> ⏱️ Done ({time.strftime('%H:%M')} - @{user})\n"
        except ValueError:
            message += f"<b>{machine_text}:</b> ❗️ Error (Status Unknown)\n"
    
    return message

def get_machines() -> List[Dict[str, str]]:
    options = []
    for machine in Machines.get_values():
        options.append({
            "label": utils.get_display_label(machine),
            "value": machine
        })
    return options

def get_machines_with_options(status: List[Status], user_id: str = None) -> List[Dict[str, str]]:
    machines = db.get_status()
    options = []
    for machine in machines:
        if (Status(machines[machine][STATUS]) in status) and (user_id is None or machines[machine][USER_ID] == user_id):
            options.append({
                "label": utils.get_display_label(machine),
                "value": machine
            })
    return options

def get_user_id(machine) -> str:
    utils.assert_valid_machine(machine)
    return db.get_user_id(machine)

def use_machine(machine, id, username):
    utils.assert_valid_machine(machine)
    db.use_machine(machine, id, username)

def is_machine_in_use(machine) -> bool:
    utils.assert_valid_machine(machine)
    return db.is_machine_in_use(machine) == "IN_USE"

def set_status(machine, status: Status):
    utils.assert_valid_machine(machine)
    db.set_status(machine, status)