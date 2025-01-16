from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

def generate_keys(private_key_path: str, public_key_path: str, passphrase: bytes = None):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    encryption_algorithm = serialization.BestAvailableEncryption(passphrase) if passphrase else serialization.NoEncryption()

    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )

    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(private_key_path, 'wb') as f:
        f.write(pem_private)
    os.chmod(private_key_path, 0o600)

    with open(public_key_path, 'wb') as f:
        f.write(pem_public)
    os.chmod(public_key_path, 0o644)

if __name__ == "__main__":
    PRIVATE_KEY_PATH = 'keys/private_key.pem'
    PUBLIC_KEY_PATH = 'keys/public_key.pem'
    PASSPHRASE = None

    os.makedirs(os.path.dirname(PRIVATE_KEY_PATH), exist_ok=True)
    generate_keys(PRIVATE_KEY_PATH, PUBLIC_KEY_PATH, PASSPHRASE)
    print("Пары ключей сгенерированы и сохранены.")
