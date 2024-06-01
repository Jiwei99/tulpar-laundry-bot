from typing import Dict
import firebase_admin
import os
from firebase_admin import db
from datetime import datetime
from constants import Status, STATUS, USER_ID, USER_USERNAME, START_TIME, CYCLE_TIME

def setup_db():
    print("Setting up Database...")
    cred_obj = firebase_admin.credentials.Certificate(
        {
            "type": os.getenv("TYPE"),
            "project_id": os.getenv("PROJECT_ID"),
            "private_key_id": os.getenv("PRIVATE_KEY_ID"),
            "private_key": os.getenv("PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("CLIENT_EMAIL"),
            "client_id": os.getenv("CLIENT_ID"),
            "auth_uri": os.getenv("AUTH_URI"),
            "token_uri": os.getenv("TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
            "universe_domain": os.getenv("UNIVERSE_DOMAIN")
        }
    )
    default_app = firebase_admin.initialize_app(cred_obj, {
        'databaseURL':os.getenv("DATABASE_URL")
    })

    print("Connected to Database!")

def get_status() -> Dict:
    print("Retrieving statuses...")
    ref = db.reference("/machines")
    status = ref.get()
    print("Statuses retrieved!")
    return status

def is_machine_in_use(machine) -> str:
    print(f"Checking {machine} status...")
    ref = db.reference(f"/machines/{machine}/{STATUS}")
    status = ref.get()
    print(f"Status for {machine} retrieved!")
    return status

def use_machine(machine, user_id, user_username, cycle_time):
    print(f"Using {machine}...")
    ref = db.reference(f"/machines/{machine}")
    ref.update({
        STATUS: Status.IN_USE.value,
        USER_ID: user_id,
        USER_USERNAME: user_username,
        START_TIME: datetime.now().isoformat(),
        CYCLE_TIME: cycle_time,
    })
    print(f"{machine} is now in use!")

def set_status(machine, status: Status):
    print(f"Finishing {machine}...")
    ref = db.reference(f"/machines/{machine}")
    ref.update({
        STATUS: status.value,
    })
    print(f"{machine} is now {status.value}!")

def get_user_id(machine) -> str:
    print(f"Retrieving user id for {machine}...")
    ref = db.reference(f"/machines/{machine}/{USER_ID}")
    user_id = ref.get()
    print(f"User id for {machine} retrieved!")
    return user_id

# from datetime import datetime
# setup_db()
# ref = db.reference("/")
# ref.set({
#     "machines": {
#         "washer_1": {
#             "status": "AVAILABLE",
#             "user_username": "",
#             "user_id": "",
#             "start_time": datetime.now().isoformat(),
#         },
#         "washer_2": {
#             "status": "AVAILABLE",
#             "user_username": "",
#             "user_id": "",
#             "start_time": datetime.now().isoformat(),
#         },
#         "dryer_1": {
#             "status": "AVAILABLE",
#             "user_username": "",
#             "user_id": "",
#             "start_time": datetime.now().isoformat(),
#         },
#         "dryer_2": {
#             "status": "AVAILABLE",
#             "user_username": "",
#             "user_id": "",
#             "start_time": datetime.now().isoformat(),
#         }
#     }
# })