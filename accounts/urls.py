from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^signup/$', views.SignupView.as_view(), name='user-signup'),
    url(r'^login/$', views.SigninView.as_view(), name='user-login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='user-logout'),
    url(r"^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$", views.ResetPasswordView.as_view(),
        name="password-reset"),
    url(r"^confirm_email/(?P<key>\w+)/$", views.EmailConfirmationView.as_view(), name="confirm-email"),
    url(r'^profile/(?P<username>\w+)$', views.ProfileView.as_view(), name='user-profile'),
    url(r'^profile/update/$', views.EditProfileView.as_view(), name='user-profile-update'),
    url(r'^api/v1', include('django-accounts.accounts.api.v1.api_urls')),
    url(r'^account/', include('account.urls'))
]
