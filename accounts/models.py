import random
import string

from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.core.validators import RegexValidator
from django.core.validators import validate_email
from django.db import models
from rest_framework.utils import model_meta

validate_phone = RegexValidator(regex=r"\d{3}-\d{3,4}-\d{4}")


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


def new_otp():
    return ''.join(random.choice(string.ascii_letters + string.digits + '!@#$%^*?') for _ in range(10))


class Authentication(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    otp = models.CharField(max_length=10, default=new_otp)
    validate_cnt = models.IntegerField(default=0)
    generate_cnt = models.IntegerField(default=0)
    generated_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'authentication'
