from itsdangerous import TimestampSigner
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


def hash_password(password):
    return generate_password_hash(password, 'pbkdf2:sha256:2000', salt_length=12)


def check_password(password, password_hash):
    return check_password_hash(password_hash, password)


def generate_token(username, secret_key):
    signer = TimestampSigner(secret_key)
    return signer.sign(username)


def validate_token(token, secret_key, max_age=None):
    signer = TimestampSigner(secret_key)
    signer.unsign(token, max_age=max_age)
