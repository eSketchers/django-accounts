from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^signup/$', views.SignupView.as_view(), name='user-signup'),
    url(r'^login/$', views.SigninView.as_view(), name='user-login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='user-logout'),
    url(r'^profile/(?P<username>\w+)$', views.ProfileView.as_view(), name='user-profile'),
    url(r'^profile/update/$', views.EditProfileView.as_view(), name='user-profile-update'),
    url(r'^api/v1', include('accounts.api.v1.api_urls')),
    url(r'^account/', include('account.urls'))
]
