import datetime

from random import randint

from django.core.validators import RegexValidator
from django.core.validators import validate_email
from django.utils import timezone
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.db import models

from rest_framework import request
from rest_framework.utils import model_meta
from rest_framework.exceptions import ValidationError

validate_phone = RegexValidator(regex=r"^\+?[0-9() -]{8,50}$")


class UserManager(BaseUserManager):

    def create_user(self, email, phone, nickname, name, password=None, **extra_fields):
        user = self.model(
            email=self.normalize_email(email),
            phone=phone,
            nickname=nickname,
            name=name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, nickname, name, password, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email),
            phone=phone,
            nickname=nickname,
            name=name,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def update_user(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        for attr, value in validated_data.items():

            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                if attr == 'password':
                    instance.set_password(value)
                else:
                    setattr(instance, attr, value)

        instance.save()

        return instance


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(max_length=50, unique=True, validators=[validate_email])
    phone = models.CharField(max_length=50, unique=True, validators=[validate_phone])
    nickname = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'nickname', 'name']

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        db_table = 'users'


class SMSVerification(models.Model):
    phone = models.CharField(max_length=50, primary_key=True, validators=[validate_phone])
    code = models.CharField(max_length=6)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'verifications'

    def save(self, *args, **kwargs):
        self.code = randint(100000, 1000000)
        super().save(*args, **kwargs)
        self.send_sms()

    def send_sms(self):
        # TODO : Connect SMS Server
        url = ''
        data = {
            "type": "SMS",
            "from": "",
            "to": self.phone,
            "content": "Verification code [{}]".format(self.code)

        }
        headers = {

        }
        # request.post(url, json=data, headers=headers)

    @classmethod
    def validate_code(cls, phone, code):
        time_delta = timezone.now() - datetime.timedelta(minutes=5)
        result = cls.objects.filter(
            phone=phone,
            code=code,
            updated__gte=time_delta
        )
        if not result:
            raise ValidationError(detail={"code": ["Enter the valid code."]})
