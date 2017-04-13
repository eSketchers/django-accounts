from account.views import SignupView as BaseSignupView, LoginView as BaseSigninView, \
    LogoutView as BaseLogoutView, PasswordResetView
from account.mixins import LoginRequiredMixin

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.views.generic import DetailView, TemplateView, FormView
from django.forms.models import model_to_dict

from .helpers import is_follower
from .forms import SignupForm, LoginForm, ProfileUpdateForm
User = get_user_model()


# Create your views here.
class SignupView(BaseSignupView):

    template_name = "signup.html"
    form_class = SignupForm

    def after_signup(self, form):
        super(SignupView, self).after_signup(form)
        self.created_user.first_name = form.cleaned_data.get('first_name', None)
        self.created_user.last_name = form.cleaned_data.get('last_name', None)
        if not settings.ACCOUNT_EMAIL_CONFIRMATION_EMAIL:
            self.created_user.is_active = True
        self.created_user.save()

    def form_valid(self, form):
        super(SignupView, self).form_valid(form)
        return redirect(reverse('user-profile', kwargs={'username': self.request.user.username}))


class SigninView(BaseSigninView):
    template_name = "login.html"
    form_class = LoginForm

    def form_valid(self, form):
        super(SigninView, self).form_valid(form)
        return redirect(reverse('user-profile', kwargs={'username': self.request.user.username}))


class LogoutView(BaseLogoutView):

    template_name = "logout.html"

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return redirect(self.get_redirect_url())
        return self.post(*args, **kwargs)


class ProfileView(DetailView):
    template_name = 'profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user'
    model = User

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context.update({'is_public_view': False})
        user = context.get('user', None)
        if user:
            if user.id == self.request.user.id:
                context['is_public_view'] = True

        context.update({
            'is_follower': is_follower(self.request.user, user),
            'followers': user.follower_set.count(),
            'followings': user.followers.count(),
            'friends': user.friends.filter(is_accepted=True).count() + user.requested_friends.filter(is_accepted=True).count()
        })
        return context


class EditProfileView(LoginRequiredMixin, FormView):
    form_class = ProfileUpdateForm
    template_name = 'edit_profile.html'
    success_url = '/'

    def get_initial(self):
        initial = super(EditProfileView, self).get_initial()
        user = model_to_dict(instance=self.request.user, exclude=('id', 'created_at', 'updated_at',
                                                                  'username', 'password',
                                                                  'is_active', 'is_superuser', 'groups',
                                                                  'is_staff', 'last_login', 'user_permissions'))
        for key, value in user.iteritems():
            initial[key] = value

        return initial

    def save_image(self, form):
        user = self.request.user
        if 'image' in form.changed_data:
            user.image = form.cleaned_data['image']
            user.save()

    def form_valid(self, form):
        changed_data = form.changed_data
        user = self.request.user
        data = {}
        for field in changed_data:
            if field not in ['image']:
                data[field] = form.cleaned_data[field]

        if data:
            User.objects.filter(pk=user.id).update(**data)
        self.save_image(form)
        return super(EditProfileView, self).form_valid(form)


class ForgetPasswordView(PasswordResetView):
    pass


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('user-profile', kwargs={'username': request.user.username}))
        return super(HomePageView, self).get(request, *args, **kwargs)



