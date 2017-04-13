from account.forms import SignupForm as BaseSignupForm, LoginUsernameForm as BaseLoginForm

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.admin import widgets

User = get_user_model()


class SignupForm(BaseSignupForm):
    first_name = forms.CharField(label=_('First Name'), max_length=255, required=True)
    last_name = forms.CharField(label=_('Last Name'), max_length=255, required=True)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.iteritems():
            field.widget.attrs.update({'placeholder': field.label})
            field.widget.attrs.update({'class': 'form-control'})


class LoginForm(BaseLoginForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.iteritems():
            field.widget.attrs.update({'placeholder': field.label})
            field.widget.attrs.update({'class': 'form-control'})


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = ('id', 'created_at', 'updated_at', 'is_active', 'is_superuser', 'is_staff', 'last_login',
                   'groups', 'user_permissions', 'username', 'password')
        use_required_attribute = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        for key, field in self.fields.iteritems():
            if type(field) == forms.DateField:
                field.widget = widgets.AdminDateWidget(attrs={'class': 'form-control has-feedback datepicker'})
            else:
                field.widget.attrs.update({'class': 'form-control has-feedback'})
            field.widget.attrs.update({'placeholder': field.label})
