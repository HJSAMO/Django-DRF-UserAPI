from django.contrib import admin
from .models import User, Authentication

# Register your models here.
admin.site.register(User)
admin.site.register(Authentication)
