import jwe
import jwt
from django.utils import timezone
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_get_secret_key, jwt_payload_handler

from accounts.models import Authentication, new_otp
from common.utils.error import APIError
from user_api.settings import SECRET_KEY, GENERATE_LIMIT, GENERATE_TERM, VALIDATE_TERM, VALIDATE_LIMIT

authentication_entity = Authentication.objects


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


def reset_login_cache(email):
    key = "/".join([email, "logintry"])
    auth = authentication_entity.filter(pk=key)
    auth.delete()


def check_try_to_login(email):
    key = "/".join([email, "logintry"])
    auth, _ = authentication_entity.get_or_create(pk=key)
    auth.validate_cnt = auth.validate_cnt + 1
    auth.save()
    return auth.validate_cnt


def reset_otp_cache(phone):
    key = "/".join([phone, "otp"])
    auth = authentication_entity.filter(key__contains=key)
    auth.delete()


def generate_otp_cache(phone, user=None):
    key = "/".join([phone, "otp"])
    auth, _ = authentication_entity.get_or_create(pk=key)
    otp = new_otp()

    if auth.generate_cnt < GENERATE_LIMIT:
        if (auth.generate_cnt > 0) and ((timezone.now() - auth.generated_date).seconds < GENERATE_TERM):
            raise APIError("REQUEST_TERM_ERROR")
    else:
        lock_user(user)
        raise APIError("COUNT_EXCEEDED_ERROR")

    auth.otp = otp
    auth.generate_cnt = auth.generate_cnt + 1
    auth.generated_date = timezone.now()
    auth.save()
    return otp


def validate_otp_cache(phone, otp, user=None):
    key = "/".join([phone, "otp"])
    auth = authentication_entity.get(pk=key)

    if (timezone.now() - auth.generated_date).seconds > VALIDATE_TERM:
        raise APIError("TIMEOUT_ERROR")

    if auth.validate_cnt >= VALIDATE_LIMIT:
        lock_user(user)
        raise APIError("COUNT_EXCEEDED_ERROR")

    if auth.otp == otp:
        if user is not None:
            auth.delete()
        return True
    else:
        auth.validate_cnt = auth.validate_cnt + 1
        auth.save()
        raise APIError("OTP_ERROR")


def lock_user(user):
    if user is not None:
        user.is_active = False
        user.save()


def send_sms(phone, otp):
    # TODO : Connect SMS Server
    url = ''
    data = {
        "type": "SMS",
        "from": "",
        "to": phone,
        "content": "Verification OTP [{}]".format(otp)

    }
    headers = {

    }
    # request.post(url, json=data, headers=headers)
