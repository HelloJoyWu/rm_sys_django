from django.conf import settings
from django.forms import ValidationError

from allauth.account.adapter import DefaultAccountAdapter


class SignUpAccountAdapter(DefaultAccountAdapter):
    """
    Customized django allauth adapter
    """

    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        allow_signups = super().is_open_for_signup(request)
        # Override with setting, otherwise default to super.
        return getattr(settings, 'ACCOUNT_ALLOW_SIGNUPS', allow_signups)

    def clean_email(self, email):
        allow_google_host = getattr(settings, 'ALLOW_SIGNUP_GOOGLE_HOST', ['adcrow.tech'])
        if email.split('@')[1].lower() not in allow_google_host:
            raise ValidationError('You are restricted from registering. Please contact admin.')
        return email
