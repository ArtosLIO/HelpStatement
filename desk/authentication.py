from datetime import datetime, timedelta

from django.utils.timezone import make_aware
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from HelpDesk.settings import AUTO_LOGOUT
from desk.models import MyToken


class TokenAuth(TokenAuthentication):
    model = MyToken

    def authenticate(self, request):
        auth = super().authenticate(request=request)
        if auth:
            user, token = auth
            if token.last_action and (make_aware(datetime.now()) - timedelta(seconds=AUTO_LOGOUT)) > token.last_action \
                    and not user.is_staff:
                msg = 'Your token has expired.'
                raise exceptions.AuthenticationFailed(msg)
            token.last_action = make_aware(datetime.now())
            token.save()
            return user, token
