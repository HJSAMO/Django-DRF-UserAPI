from django.contrib import admin
from .models import User, SMSVerification

# Register your models here.
admin.site.register(User)
admin.site.register(SMSVerification)
