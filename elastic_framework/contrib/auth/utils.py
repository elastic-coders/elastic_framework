from datetime import date
from oauth2_provider.models import AccessToken
from django.core.exceptions import PermissionDenied

def create_token(user, app):
    token = AccessToken(application=app, user=user)
    # TODO: make this better for not expiring token 
    # and permitting to set expiring from application settings
    token.expires = date(2099, 12, 31)
    token.save()
    return token


def get_token(user, client):
    try:
        token = AccessToken.objects.get(client=client, user=user)
    except AccessToken.DoesNotExist:
        return None
    return token

def get_token_from_request(request):
    try:
        token = request.META['HTTP_AUTHORIZATION']
    except:
        raise PermissionDenied()
    return token[7:]
