from datetime import datetime
from pathlib import Path
from keys.asymetric_keys import sign, verify
from cryptography.hazmat.primitives import serialization
from jwt_wrapper import authenticate, decode, check_expired

def get_keys():
    private_key_bytes = Path('./keys/private_key.pem').read_bytes()
    public_key_data = Path('./keys/public_key.pem').read_bytes()
    
    private_key = serialization.load_pem_private_key(
        private_key_bytes,
        b"my secret"
    )
    
    public_key = serialization.load_pem_public_key(public_key_data)
    
    return private_key, public_key

def get_token(user, password):
    return authenticate(user, password)

def test_sign():
    signature = sign(b"TOP SECRET MESSAGE", get_keys()[0])
    assert signature is not None
    
def test_verify():
    signature = sign(b"TOP SECRET MESSAGE", get_keys()[0])
    verification = verify(
        signature,
        b"TOP SECRET MESSAGE",
        get_keys()[1]
    )
    assert verification == "The message has been successfully verified"
    
def test_verify_fails():
    signature = sign(b"TOP SECRET MESSAGE", get_keys()[0])
    verification = verify(
        signature,
        b"NOT SO SECRET",
        get_keys()[1]
    )
    assert verification == "The signature, the message or the Public Key is invalid"
    
def test_valid_authentication():
    token = get_token("admin", "password")
    assert token is not None
    
def test_invalid_authentication():
    token = get_token("user1", "pass1")
    assert token is None
    
def test_decoded_token():
    token = get_token("admin", "password")
    decoded = decode(token)
    assert decoded is not None
    assert decoded != token
    
def test_check_expired():
    current_time = datetime.now()
    token_expiry = datetime.fromtimestamp(decode(get_token("admin", "password"))['exp'])
    assert current_time < token_expiry