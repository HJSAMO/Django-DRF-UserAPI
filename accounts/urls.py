from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'accounts'

urlpatterns = [
    url(r'^signup/?$', views.SignUpView.as_view()),
    url(r'^login/?$', views.LoginView.as_view()),
    url(r'^info/?$', views.UserInfoView.as_view()),
    url(r'^generation/?$', views.GenerationView.as_view()),
    url(r'^verification/?$', views.VerificationView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
