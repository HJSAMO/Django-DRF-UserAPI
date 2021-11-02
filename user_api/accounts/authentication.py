import jwt
import jwe

from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_get_secret_key, jwt_payload_handler

from user_api.settings import SECRET_KEY


def jwt_decode_handler(token):
    decrypted_token = jwt.decrypt(token, _get_derived_key())
    token = decrypted_token
    options = {
        'verify_exp': api_settings.JWT_VERIFY_EXPIRATION,
    }
    unverified_payload = jwt.decode(token, None, False)
    secret_key = jwt_get_secret_key(unverified_payload)
    return jwt.decode(token, secret_key, options=options)


def generate_jwt_token(user):
    payload = jwt_payload_handler(user)
    return _build_token_info(user, payload)


def _build_token_info(user, payload):
    token = jwt.encode(payload, jwt_get_secret_key(payload))
    encrypted_token = jwe.encrypt(token, _get_derived_key())

    login_user = {
        'email': user.email,
        'phone': user.phone,
        'nickname': user.nickname,
        'name': user.name,
        'token': encrypted_token.decode('utf8'),
    }

    return login_user


def _get_derived_key():
    system_key = SECRET_KEY.encode(encoding='utf_8', errors='strict')
    salt = b'pepper'
    return jwe.kdf(system_key, salt)
