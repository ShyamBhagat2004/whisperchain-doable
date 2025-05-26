# test_week2.py

from user_registration import get_role_from_userid
from token_manager import issue_token_for_user, validate_token, use_token
from role_permissions import has_permission
from action_logger import log_event, read_all_logs

import uuid
import json
import os

DATA_FILE = "storage.json"

def run_all_tests():
    print("\n--- running full week 2 test ---")

    # Step 1: Register users with different roles
    print("\n[1] registering users...")
    sender_id = register_user_sim("Sender")
    mod_id = register_user_sim("Moderator")
    recipient_id = register_user_sim("Recipient")

    # Step 2: Try issuing token as Sender
    print("\n[2] issuing token as Sender (should work)")
    token1 = issue_token_for_user(sender_id)
    log_event("Sender", "TokenIssued")

    # Step 3: Try issuing another token same round (should fail)
    print("\n[3] issuing another token as same Sender (should fail)")
    token2 = issue_token_for_user(sender_id)  # should print warning

    # Step 4: Validate and use token
    print("\n[4] validating and using token")
    if validate_token(token1):
        use_token(token1)
        log_event("Sender", "MessageSent")

    # Step 5: Try reusing same token (should fail)
    print("\n[5] try reusing same token (should fail)")
    if not validate_token(token1):
        print("√ double-use protection works")

    # Step 6: View logs as Moderator (should work)
    print("\n[6] Moderator viewing logs")
    if has_permission("Moderator", "view_logs"):
        logs = read_all_logs()
        print("last few log lines:")
        for line in logs[-5:]:
            print(" ", line.strip())

    # Step 7: Try unauthorized log access (Recipient, should fail)
    print("\n[7] Recipient trying to view logs (should be blocked)")
    if not has_permission("Recipient", "view_logs"):
        print("√ access blocked correctly")

    print("\n √ ALL BASIC TESTS COMPLETED")


# helper to simulate user registration with role
def register_user_sim(role):
    user_id = str(uuid.uuid4())
    print(f"  created user with ID: {user_id} and role: {role}")

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    if "users" not in data:
        data["users"] = {}

    data["users"][user_id] = {
        "role": role
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return user_id


if __name__ == "__main__":
    run_all_tests()
