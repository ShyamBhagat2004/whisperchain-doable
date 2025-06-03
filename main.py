from user_registration import register_user, get_role_from_userid, get_user_entry
from token_manager import issue_token_for_user, validate_token, use_token, freeze_token, is_token_frozen
from role_permissions import has_permission
from action_logger import log_event, read_all_logs
from crypto_utils import encrypt_message, decrypt_message, reencrypt_message_for_moderator
import uuid
import json
import os
from datetime import datetime

DATA_FILE = "storage.json"

def main():
    print("\n--- Week 4, whisperchain project, unemployed men in the middle---")

    while True:
        print("\n Here are the options:")
        print("1. register a new user")
        print("2. issue token (sender only)")
        print("3. use a token")
        print("4. View all logs (mod/sysadmin)")
        print("5. send encrypted message")
        print("6. read + decrypt your messages")
        print("7. flag a message")
        print("8. view flagged messages (mod only)")
        print("9. freeze a token (mod only)")
        print("10. ban a user by message ID (mod only)")
        print("11. Exit the program")

        choice = input("what do you want to do? Choose a number, wisely ... ").strip()

        if choice == "1":
            user_id = register_user()
            if user_id:
                print(f"user {user_id} registered successfully.")

        elif choice == "2":
            user_id = input("enter your user ID: ").strip()
            data = load_data()
            blocked_users = data.get("blocked_users", [])
            if user_id in blocked_users:
                print("you have been banned from sending messages.")
                continue

            role = get_role_from_userid(user_id)
            if not role:
                continue

            if not has_permission(role, "issue_token"):
                print("you are not allowed to get a token.")
                continue

            token = issue_token_for_user(user_id)
            if token:
                log_event(role, "TokenIssued")

        elif choice == "3":
            token = input("paste your token here: ").strip()
            if validate_token(token):
                use_token(token)
                print("token accepted and it has been marked as used.")
                log_event("Sender", "MessageSent (simulated)")
            else:
                print("token was invalid or already used. Sorry bro...")

        elif choice == "4":
            user_id = input("enter your user ID: ").strip()
            role = get_role_from_userid(user_id)
            if not role:
                continue

            if not has_permission(role, "view_logs"):
                print("sorry, you are not allowed to view logs.")
                continue

            logs = read_all_logs()
            print("\n--- logs below ---")
            for line in logs:
                print(line.strip())

        elif choice == "5":
            sender_id = input("enter your user ID (sender): ").strip()
            data = load_data()
            blocked_users = data.get("blocked_users", [])
            if sender_id in blocked_users:
                print("you have been banned from sending messages.")
                continue

            sender = get_user_entry(sender_id)
            if not sender or sender.get("role") != "Sender":
                print("only Senders can send messages.")
                continue

            token = input("enter your token to send a message: ").strip()
            if not validate_token(token):
                print("token was invalid or already used. can't send.")
                continue
            if is_token_frozen(token):
                print("this token has been frozen. you can't send anything.")
                continue

            recipient_id = input("enter the recipient’s user ID: ").strip()
            recipient = get_user_entry(recipient_id)
            if not recipient:
                print("recipient not found.")
                continue

            msg = input("type your message (this will be encrypted): ").strip()
            public_key = recipient["public_key"]
            encrypted = encrypt_message(msg, public_key)

            if "messages" not in data:
                data["messages"] = {}

            msg_id = str(uuid.uuid4())
            data["messages"][msg_id] = {
                "recipient_id": recipient_id,
                "ciphertext": encrypted,
                "sender_id": sender_id,
                "timestamp": datetime.utcnow().isoformat(),
                "flagged": False
            }

            save_data(data)
            use_token(token)
            log_event("Sender", "MessageSent")
            print("encrypted message saved successfully.")

        elif choice == "6":
            user_id = input("enter your user ID: ").strip()
            user = get_user_entry(user_id)
            if not user:
                print("user not found.")
                continue

            data = load_data()
            messages = data.get("messages", {})
            found = 0

            for msg_id, msg in messages.items():
                if msg["recipient_id"] == user_id:
                    print("\n--- message ID:", msg_id, "---")
                    try:
                        decrypted = decrypt_message(msg["ciphertext"], user["private_key"])
                        print("sent at:", msg["timestamp"])
                        print("content:", decrypted)
                        print("flagged:", msg.get("flagged", False))
                        found += 1
                        log_event("Recipient", "MessageRetrieved")
                    except:
                        print("couldn’t decrypt this one.")
            if found == 0:
                print("you have no messages.")

        elif choice == "7":
            user_id = input("enter your user ID (recipient): ").strip()
            user = get_user_entry(user_id)
            if not user or user["role"] != "Recipient":
                print("only recipients can flag.")
                continue

            msg_id_input = input("enter full or partial message ID to flag: ").strip()
            data = load_data()
            matched_ids = [mid for mid in data.get("messages", {}) if mid.startswith(msg_id_input)]
            if len(matched_ids) == 0:
                print("message not found.")
                continue
            elif len(matched_ids) > 1:
                print("multiple messages matched.")
                continue

            msg_id = matched_ids[0]
            msg = data["messages"][msg_id]
            if msg["recipient_id"] != user_id:
                print("you can only flag your own messages.")
                continue

            msg["flagged"] = True
            save_data(data)
            log_event("Recipient", "MessageFlagged")
            print("message flagged.")

        elif choice == "8":
            user_id = input("enter your user ID (moderator): ").strip()
            moderator = get_user_entry(user_id)
            if not moderator or moderator["role"] != "Moderator":
                print("only moderators can see the mess.")
                continue

            data = load_data()
            flagged = {mid: msg for mid, msg in data.get("messages", {}).items() if msg.get("flagged")}
            if not flagged:
                print("no flagged messages.")
            else:
                for mid, msg in flagged.items():
                    print("\nflagged msg ID:", mid[:8])
                    print("timestamp:", msg["timestamp"])

                    recipient_id = msg["recipient_id"]
                    recipient = get_user_entry(recipient_id)
                    if not recipient:
                        print("couldn't find recipient.")
                        continue

                    try:
                        reencrypted_hex = reencrypt_message_for_moderator(
                            msg["ciphertext"],
                            recipient["private_key"],
                            moderator["public_key"]
                        )
                        decrypted_for_mod = decrypt_message(reencrypted_hex, moderator["private_key"])
                        print("content for moderator:", decrypted_for_mod)
                        log_event("Moderator", "FlaggedMessageReviewed")
                    except:
                        print("couldn't decrypt flagged message.")

        elif choice == "9":
            user_id = input("enter your user ID: ").strip()
            user = get_user_entry(user_id)
            if not user or user["role"] != "Moderator":
                print("you’re not a mod. freeze denied.")
                continue

            token = input("enter token to freeze: ").strip()
            success = freeze_token(token)
            if success:
                log_event("Moderator", "TokenFrozen")
                print("token frozen.")
            else:
                print("couldn’t freeze.")

        elif choice == "10":
            user_id = input("enter your user ID (moderator): ").strip()
            moderator = get_user_entry(user_id)
            if not moderator or moderator["role"] != "Moderator":
                print("you’re not a mod. ban denied.")
                continue

            msg_id = input("enter the message ID to ban the sender of: ").strip()
            data = load_data()
            msg = data.get("messages", {}).get(msg_id)
            if not msg:
                print("message not found.")
                continue

            sender_id = msg.get("sender_id")
            if not sender_id:
                print("no sender recorded for this message.")
                continue

            if "blocked_users" not in data:
                data["blocked_users"] = []
            if sender_id not in data["blocked_users"]:
                data["blocked_users"].append(sender_id)
                save_data(data)
                log_event("Moderator", f"UserBanned (via message): {msg_id}")
                print("sender has been banned. (we’re not showing who)")
            else:
                print("sender already banned.")

        elif choice == "11":
            print("OK, exiting the program.")
            break

        else:
            print("huh? try 1-11.")

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("storage.json was empty or busted. fixing it.")
            return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    main()
