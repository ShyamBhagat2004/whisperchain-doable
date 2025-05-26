import uuid
import json
import os

# WEEK 3: we now need key generation
from crypto_utils import generate_keypair  # handles RSA stuff

DATA_FILE = "storage.json"

# register a user, assign them a role, and now also give them keys (WEEK 3)
def register_user():
    print("\nstarting user registration...")

    role = input("enter a role (Sender, Recipient, Moderator, Sysadmin): ").strip()

    if role not in ["Sender", "Recipient", "Moderator", "Sysadmin"]:
        print("invalid role. try again.")
        return None

    user_id = str(uuid.uuid4())
    print("your user id is:", user_id)

    # WEEK 3: generate public/private keypair
    public_key, private_key = generate_keypair()

    data = load_data()

    if "users" not in data:
        data["users"] = {}

    # store everything in one place, including keys (WEEK 3)
    data["users"][user_id] = {
        "role": role,
        "public_key": public_key,    # WEEK 3
        "private_key": private_key   # WEEK 3
    }

    save_data(data)
    print("user saved successfully (keys included).")
    return user_id

# get the user's role by their ID (used in permission checks)
def get_role_from_userid(user_id):
    data = load_data()
    user_info = data.get("users", {}).get(user_id)
    if user_info:
        return user_info.get("role")
    else:
        print("couldn’t find user id:", user_id)
        return None

# WEEK 3: get full user data  used when accessing keys
def get_user_entry(user_id):
    data = load_data()
    return data.get("users", {}).get(user_id)

# load from disk
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("storage.json was blank or messy. starting clean.")
            return {}

# write back to disk
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
# test stuff for this file
if __name__ == "__main__":
    print("running a quick test for user registration...\n")

    user_id = register_user()
    if not user_id:
        print("registration failed, try again.")
    else:
        print("\nchecking role and keys for new user...")
        role = get_role_from_userid(user_id)
        entry = get_user_entry(user_id)

        print("role:", role)
        print("public key preview:\n", entry.get("public_key", "")[:80], "...")
        print("private key preview:\n", entry.get("private_key", "")[:80], "...")

        if role and "public_key" in entry and "private_key" in entry:
            print("\nYES looks good. user registered with role + keys.")
        else:
            print("\nNO something went wrong. oof.")
