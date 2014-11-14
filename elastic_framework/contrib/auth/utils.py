from provider.oauth2.models import AccessToken
from django.core.exceptions import PermissionDenied

def create_token(user, client):
    token = AccessToken(client=client, user=user)
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
    return token[:7]
