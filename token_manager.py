import uuid
import json
import os

# storing everything in this file for now, same as users
DATA_FILE = "storage.json"
ROUND = 1  # we’re just hardcoding round number here for now

# gives a user a new token if they don’t already have one this round
def issue_token_for_user(user_id):
    data = load_data()

    if "tokens" not in data:
        data["tokens"] = {}

    # double check they didn’t already get one this round
    for tkn, info in data["tokens"].items():
        if info.get("user_id") == user_id and info.get("round") == ROUND:
            print("you already got a token this round. can’t give another one. greedy aah")
            return None

    token = str(uuid.uuid4())
    data["tokens"][token] = {
        "user_id": user_id,
        "used": False,
        "round": ROUND
    }

    save_data(data)
    print("issued token:", token)
    return token

# checks if the token is valid (exists + not used)
def validate_token(token):
    data = load_data()

    if "tokens" not in data or token not in data["tokens"]:
        print("token not found or doesn’t exist")
        return False

    if data["tokens"][token]["used"]:
        print("that token was already used")
        return False

    return True

# marks the token as used (only if it exists)
def use_token(token):
    data = load_data()

    if token in data.get("tokens", {}):
        data["tokens"][token]["used"] = True
        save_data(data)
    else:
        print("tried to use a token that’s not there")

# helper function to load everything from disk
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError: #this was happening a bit when we started coding this, but now doesn't really happen anymore
            print("file was empty or kinda broken. starting fresh.")
            return {}

# saves to disk
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
# WEEK 4: freeze a token
def freeze_token(token_id):
    data = load_data()
    if "tokens" in data and token_id in data["tokens"]:
        data["tokens"][token_id]["frozen"] = True
        save_data(data)
        return True
    return False

# WEEK 4: check if token is frozen
def is_token_frozen(token_id):
    data = load_data()
    return data.get("tokens", {}).get(token_id, {}).get("frozen", False)
