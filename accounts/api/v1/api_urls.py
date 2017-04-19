from django.conf.urls import url

from . import api_views

urlpatterns = [
    url(r'login/$', api_views.LoginAPIView.as_view(), name='login'),
    url(r'social-auth/$', api_views.SocialAuthAPIView.as_view(), name='social-auth'),
    url(r'sign-up/$', api_views.SignupAPIView.as_view(), name='sign-up'),
    url(r'change-password/$', api_views.ChangePasswordAPIView.as_view(), name='change-password'),
    url(r'forget-password/$', api_views.ForgotPasswordAPIView.as_view(), name='forget-password'),
    url(r'reset-password/$', api_views.ResetPasswordAPIView.as_view(), name='reset-password'),
]