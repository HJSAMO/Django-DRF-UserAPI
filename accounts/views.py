import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from rest_framework.exceptions import ValidationError as DRFValidationError

from .authentication import generate_jwt_token
from .models import User, SMSVerification
from .serializers import UserSerializer, UserInfoSerializer


class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            email = data['email']
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

            if user is None:
                return JsonResponse({'CODE': 'INVALID_USER'}, status=400)

            login_user = generate_jwt_token(user)
            login(request, user)

            return JsonResponse({'USER': login_user, 'CODE': 'SUCCESS'}, status=200)
        except KeyError:
            return JsonResponse({'CODE': 'KEY_ERROR'}, status=400)


class UserInfoView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            phone = data['phone']
            code = data['code']
            password = data['password']

            validate_password(password)
            SMSVerification.validate_code(phone, code)

            user = User.objects.get(phone=phone)
            user_serializer = UserSerializer(user, data={'password': password}, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()
                return JsonResponse({'CODE': 'SUCCESS'}, status=200)
            else:
                return JsonResponse({'CODE': 'FAIL'}, status=400)

        except KeyError:
            return JsonResponse({'CODE': 'KEY_ERROR'}, status=400)
        except ValidationError as ve:
            return JsonResponse({'CODE': 'VALIDATION_ERROR', 'MESSAGE': {'password': ve.messages}}, status=400)
        except DRFValidationError as dve:
            return JsonResponse({'CODE': 'VALIDATION_ERROR', 'MESSAGE': dve.detail}, status=400)

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
            SMSVerification.objects.update_or_create(phone=phone)
            return JsonResponse({'CODE': 'SUCCESS'}, status=200)
        except KeyError:
            return JsonResponse({'CODE': 'KEY_ERROR'}, status=400)


class VerificationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone = data['phone']
            code = data['code']
            SMSVerification.validate_code(phone, code)
            return JsonResponse({'CODE': 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'CODE': 'KEY_ERROR'}, status=400)
        except DRFValidationError as dve:
            return JsonResponse({'CODE': 'VALIDATION_ERROR', 'MESSAGE': dve.detail}, status=400)
