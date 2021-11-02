import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login

from .authentication import generate_jwt_token
from .models import User, SMSVerification
from .serializers import UserSerializer, UserInfoSerializer
from .utils import validate_email, validate_password


class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            email = data['email']
            phone = data['phone']
            password = data['password']
            nickname = data['nickname']
            name = data['name']

            if not validate_email(email):
                return JsonResponse({'MESSAGE': 'INVALID_EMAIL'}, status=400)

            if not validate_password(password):
                return JsonResponse({'MESSAGE': 'INVALID_PASSWORD'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'MESSAGE': 'DUPLICATE_EMAIL'}, status=400)

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'MESSAGE': 'DUPLICATE_PHONE'}, status=400)

            if User.objects.filter(nickname=nickname).exists():
                return JsonResponse({'MESSAGE': 'DUPLICATE_NICKNAME'}, status=400)

            user_serializer = UserSerializer(data={
                'email': email,
                'phone': phone,
                'password': password,
                'nickname': nickname,
                'name': name
            })
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()
                return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)
            else:
                return JsonResponse({'MESSAGE': 'INVALID_USER'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)


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
                return JsonResponse({'MESSAGE': 'INVALID_USER'}, status=400)

            login_user = generate_jwt_token(user)
            login(request, user)

            return JsonResponse({'USER': login_user, 'MESSAGE': 'SUCCESS'}, status=200)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)


class UserInfoView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            phone = data['phone']
            code = data['code']
            password = data['password']

            if not SMSVerification.check_code(phone, code):
                return JsonResponse({'MESSAGE': 'FAIL'}, status=400)

            if not validate_password(password):
                return JsonResponse({'MESSAGE': 'INVALID_PASSWORD'}, status=400)

            user = User.objects.get(phone=phone)
            user_serializer = UserSerializer(user, data={'password': password}, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()
                return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)
            else:
                return JsonResponse({'MESSAGE': 'FAIL'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

    @method_decorator(login_required)
    def get(self, request):
        user_info = UserInfoSerializer({'email': request.user.email,
                                        'phone': request.user.phone,
                                        'nickname': request.user.nickname,
                                        'name': request.user.name}).data
        return JsonResponse({'USER': user_info, 'MESSAGE': 'SUCCESS'}, status=200)


class GenerationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone = data['phone']
            SMSVerification.objects.update_or_create(phone=phone)
            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)


class VerificationView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone = data['phone']
            code = data['code']
            if SMSVerification.check_code(phone, code):
                return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)
            else:
                return JsonResponse({'MESSAGE': 'FAIL'}, status=400)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
