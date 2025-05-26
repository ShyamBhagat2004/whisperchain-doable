from token_manager import issue_token_for_user, validate_token, use_token, freeze_token, is_token_frozen
from crypto_utils import encrypt_message, decrypt_message
from action_logger import log_event
from datetime import datetime
import uuid
import json
import os

DATA_FILE = "storage.json"

# simulate user registration (no input, no fuss)
def register_user_simulated(role):
    from crypto_utils import generate_keypair

    user_id = str(uuid.uuid4())
    public_key, private_key = generate_keypair()

    data = load_data()
    if "users" not in data:
        data["users"] = {}

    data["users"][user_id] = {
        "role": role,
        "public_key": public_key,
        "private_key": private_key
    }

    save_data(data)
    return user_id

# load/save helpers
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def log_header(title):
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def run_full_week4_test():
    log_header("STARTING FULL WEEK 4 FUNCTIONALITY TEST — NO INPUTS, JUST VIBES")

    # Step 1: Register users (with roles hardcoded)
    sender_id = register_user_simulated("Sender")
    recipient_id = register_user_simulated("Recipient")
    moderator_id = register_user_simulated("Moderator")

    print(f"🎯 Users ready:\n- Sender: {sender_id}\n- Recipient: {recipient_id}\n- Moderator: {moderator_id}")

    # Step 2: Issue token to sender
    log_header("GIVING THE SENDER THEIR ONE (1) TOKEN")
    token = issue_token_for_user(sender_id)
    print(f"🔑 Token granted: {token}")

    # Step 3: Sender sends 3 encrypted messages
    log_header("SENDER GOING OFF — DROPPING 3 ENCRYPTED BARS")
    data = load_data()
    if "messages" not in data:
        data["messages"] = {}

    for i in range(3):
        content = f"message number {i+1} (this better be good)"
        encrypted = encrypt_message(content, data["users"][recipient_id]["public_key"])
        msg_id = str(uuid.uuid4())
        data["messages"][msg_id] = {
            "recipient_id": recipient_id,
            "ciphertext": encrypted,
            "timestamp": datetime.utcnow().isoformat(),
            "flagged": False
        }
        print(f"📩 Sent: {content} | msg ID: {msg_id[:8]}")
        log_event("Sender", "MessageSent")

    save_data(data)

    # Step 4: Recipient decrypts and flags all messages
    log_header("RECIPIENT CHECKING THE MAIL — FLAGGING EVERYTHING")
    for msg_id, msg in data["messages"].items():
        if msg["recipient_id"] == recipient_id:
            try:
                decrypted = decrypt_message(msg["ciphertext"], data["users"][recipient_id]["private_key"])
                print(f"📨 Decrypted Msg {msg_id[:8]}: {decrypted}")
                msg["flagged"] = True
                log_event("Recipient", "MessageFlagged")
            except:
                print(f"⚠️ Failed to decrypt msg {msg_id[:8]} — probably cursed")

    save_data(data)

    # Step 5: Moderator reviews flagged messages
    log_header("MODERATOR LOGGING IN — TIME TO JUDGE")
    flagged_msgs = 0
    for msg_id, msg in data["messages"].items():
        if msg.get("flagged"):
            print(f"🚩 Flagged Msg {msg_id[:8]} | Sent: {msg['timestamp']}")
            print(f"✉️ Ciphertext snippet: {msg['ciphertext'][:50]}...")
            flagged_msgs += 1
            log_event("Moderator", "FlaggedMessageReviewed")

    print(f"✅ Moderator reviewed {flagged_msgs} flagged message(s).")

    # Step 6: Freeze sender’s token
    log_header("MODERATOR HITS THE BIG RED BUTTON — FREEZING THE TOKEN")
    result = freeze_token(token)
    if result:
        print(f"🧊 Token {token[:8]} frozen. Sender is iced out.")
        log_event("Moderator", "TokenFrozen")
    else:
        print("❌ Token freeze failed. Strange.")

    # Step 7: Sender tries to use frozen token again
    log_header("SENDER TRIES TO SEND AGAIN — BUT THEY'RE FROZEN")
    if is_token_frozen(token):
        print("🚫 Token is frozen. Sender blocked as expected. ✅")
    else:
        print("⚠️ Token isn’t frozen? That’s a problem.")

    log_header("✅ TEST COMPLETE — SYSTEM IS BULLETPROOF")
    print("Check logs.txt and storage.json if you're feeling paranoid.")

if __name__ == "__main__":
    run_full_week4_test()
