from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

###### Signing messages

def sign(message, private_key):
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

###### Verifyging siganture
def verify(signature, message, public_key):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        #Change to true or false
        return "The message has been successfully verified"
    except InvalidSignature:
        return "The signature, the message or the Public Key is invalid"

if __name__ == '__main__':
    print('|[ Generating Asymetric Keys ]|')
    
    # Generating keys
    key_size = 2048  # Should be at least 2048

    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Do not change
        key_size=key_size,
    )

    public_key = private_key.public_key()
    
    #######Storing private key

    password = b"my secret"

    key_pem_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,  # PEM Format is specified
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(password),
    )

    # Filename could be anything
    key_pem_path = Path("private_key.pem")
    key_pem_path.write_bytes(key_pem_bytes)
    
    ###### Storing public key
    public_key = private_key.public_key()

    public_pem_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Filename could be anything
    public_pem_path = Path("public_key.pem")
    public_pem_path.write_bytes(public_pem_bytes)