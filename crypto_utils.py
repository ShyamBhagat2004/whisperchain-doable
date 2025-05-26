from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes


# makes a public/private keypair
def generate_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048  # big enough to be safe
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    return public_pem, private_pem


# encrypts a message using the recipient’s public key
def encrypt_message(plaintext, recipient_public_key_pem):
    public_key = serialization.load_pem_public_key(
        recipient_public_key_pem.encode("utf-8")
    )

    secret_text = public_key.encrypt(
        plaintext.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return secret_text.hex()  # return as hex string for easy JSON storage


# decrypts a message using the private key
def decrypt_message(secret_text_hex, private_key_pem):
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"),
        password=None
    )

    secret_text_bytes = bytes.fromhex(secret_text_hex)

    plaintext = private_key.decrypt(
        secret_text_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return plaintext.decode("utf-8")


# NEW: re-encrypt a message for moderator viewing
def reencrypt_message_for_moderator(ciphertext_hex, recipient_private_key_pem, moderator_public_key_pem):
    # Decrypt the original message with recipient’s private key
    decrypted_text = decrypt_message(ciphertext_hex, recipient_private_key_pem)

    # Encrypt the plaintext for the moderator’s public key
    reencrypted_hex = encrypt_message(decrypted_text, moderator_public_key_pem)
    return reencrypted_hex


# quick test to ensure this file is working
if __name__ == "__main__":
    print("running a quick crypto test...")

    msg = "this is a secret"
    print("original message:", msg)

    pub, priv = generate_keypair()
    print("\npublic key:\n", pub[:64], "...")
    print("private key:\n", priv[:64], "...")

    encrypted = encrypt_message(msg, pub)
    print("\nmessage was encrypted as:\n", encrypted[:64], "...")

    decrypted = decrypt_message(encrypted, priv)
    print("\nmessage decrypted as:", decrypted)

    if decrypted == msg:
        print("YES encryption/decryption works")
    else:
        print("NO something went wrong")
