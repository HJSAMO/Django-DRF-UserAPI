import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.exceptions import ValidationError as DRFValidationError

from common.utils.error import APIError
from user_api.settings import LOGIN_LIMIT
from .authentication import generate_jwt_token, check_try_to_login, lock_user, reset_login_cache, validate_otp_cache, \
    reset_otp_cache, generate_otp_cache, send_sms
from .models import User, UserManager
from .serializers import UserSerializer, UserInfoSerializer

user_manager = UserManager()
user_entity = User.objects


class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            email = user_manager.normalize_email(data['email'])
            phone = data['phone']
            password = data['password']
            nickname = data['nickname']
            name = data['name']

            validate_password(password)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'CODE': 'DUPLICATE_EMAIL'}, status=400)

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'CODE': 'DUPLICATE_PHONE'}, status=400)

            if User.objects.filter(nickname=nickname).exists():
                return JsonResponse({'CODE': 'DUPLICATE_NICKNAME'}, status=400)

            user_serializer = UserSerializer(data={
                'email': email,
                'phone': phone,
                'password': password,
                'nickname': nickname,
                'name': name
            })
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()
                return JsonResponse({'CODE': 'SUCCESS'}, status=200)
            else:
                return JsonResponse({'CODE': 'INVALID_USER'}, status=400)

        except KeyError:
            return JsonResponse({'CODE': 'KEY_ERROR'}, status=400)
        except ValidationError as ve:
            return JsonResponse({'CODE': 'VALIDATION_ERROR', 'MESSAGE': {'password': ve.messages}}, status=400)
        except DRFValidationError as dve:
            return JsonResponse({'CODE': 'VALIDATION_ERROR', 'MESSAGE': dve.detail}, status=400)
        except APIError as e:
            return JsonResponse({'CODE': e.value}, status=500)


class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email_or_phone = data['email_or_phone']
            password = data['password']

            email_by_phone = User.objects.filter(phone=email_or_phone)
            if email_by_phone.exists():
                email_or_phone = email_by_phone[0].email

            user = authenticate(email=email_or_phone, password=password)
            login_try_cnt = check_try_to_login(email_or_phone)

            if login_try_cnt >= LOGIN_LIMIT:
                user = user_entity.get(email=email_or_phone)
                lock_user(user)
            if user is None:
                return JsonResponse({'CODE': 'INVALID_USER'}, status=400)
            if not user.is_active:
                return JsonResponse({'CODE': 'LOCKED_USER'}, status=400)

            login_user = generate_jwt_token(user)
            reset_login_cache(user.email)
            login(request, user)

            if user.is_superuser is True or user.is_active:
                return JsonResponse({'USER': login_user, 'CODE': 'SUCCESS'}, status=200)
            else:
                return JsonResponse({'CODE': 'UNAUTHORIZED'}, status=401)
        except KeyError:
            return JsonResponse({'CODE': 'KEY_ERROR'}, status=400)
        except APIError as e:
            return JsonResponse({'CODE': e.value}, status=500)


class UserInfoView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            phone = data['phone']
            otp = data['otp']
            password = data['password']

            if not User.objects.filter(phone=phone).exists():
                return JsonResponse({'CODE': 'INVALID_USER'}, status=400)

            validate_password(password)
            user = User.objects.get(phone=phone)

            validated = validate_otp_cache(phone, otp, user)
            if validated:
                reset_otp_cache(phone)
                user_serializer = UserSerializer(
                    user, data={'password': password, 'is_active': True}, partial=True)
                if user_serializer.is_valid(raise_exception=True):
                    user_serializer.save()
                    return JsonResponse({'CODE': 'SUCCESS'}, status=200)
            return JsonResponse({'CODE': 'FAIL'}, status=400)

        except KeyError:
            return JsonResponse({'CODE': 'KEY_ERROR'}, status=400)
        except ValidationError as ve:
            return JsonResponse({'CODE': 'VALIDATION_ERROR', 'MESSAGE': {'password': ve.messages}}, status=400)
        except DRFValidationError as dve:
            return JsonResponse({'CODE': 'VALIDATION_ERROR', 'MESSAGE': dve.detail}, status=400)
        except APIError as e:
            return JsonResponse({'CODE': e.value}, status=500)

    @method_decorator(login_required)
    def get(self, request):
        user_info = UserInfoSerializer({'email': request.user.email,
                                        'phone': request.user.phone,
                                        'nickname': request.user.nickname,
                                        'name': request.user.name}).data
        return JsonResponse({'USER': user_info, 'CODE': 'SUCCESS'}, status=200)


class GenerationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone = data['phone']
            otp = generate_otp_cache(phone)
            send_sms(phone, otp)
            return JsonResponse({'temp_otp_for_test': otp, 'CODE': 'SUCCESS'}, status=200)
            # TODO : Change logic after SMS Server Connected
            # return JsonResponse({'CODE': 'SUCCESS'}, status=200)
        except KeyError:
            return JsonResponse({'CODE': 'KEY_ERROR'}, status=400)
        except APIError as e:
            return JsonResponse({'CODE': e.value}, status=500)


class VerificationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone = data['phone']
            otp = data['otp']
            validate_otp_cache(phone, otp)
            return JsonResponse({'CODE': 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'CODE': 'KEY_ERROR'}, status=400)
        except DRFValidationError as dve:
            return JsonResponse({'CODE': 'VALIDATION_ERROR', 'MESSAGE': dve.detail}, status=400)
        except APIError as e:
            return JsonResponse({'CODE': e.value}, status=500)
