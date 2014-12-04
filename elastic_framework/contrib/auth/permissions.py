from rest_framework.exceptions import PermissionDenied

def check_user_is_owner(user, request):
    ''' Check if user request is the owner of the requested entity
    if not it raise an exception
    '''
    if not user == request.user:
        raise PermissionDenied()
