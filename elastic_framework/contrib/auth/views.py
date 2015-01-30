
import logging
import uuid

from django.db import transaction
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from rest_framework.generics import (GenericAPIView, ListCreateAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework import permissions
from rest_framework import status

from provider.oauth2.models import AccessToken, Client

from elastic_framework.core.exceptions import APIError

from .serializers import (ECUserSignupSerializer, ECUserResponseSerializerClass,
                          ECUserSerializer)
from .utils import create_token, get_token_from_request
from .permissions import check_user_is_owner
from .facebook import facebook_authentication
from .api import get_base_field_user_model


logger = logging.getLogger(__name__)

class Oauth2ECUserListView(GenericAPIView):
    '''Base view for user signup using oauth2 authentication method

    '''
    signup_serializer_class = ECUserSignupSerializer
    serializer_class = ECUserResponseSerializerClass
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    token = {}
    authentication_type = ''

    def get_queryset(self):
        return get_user_model().objects.all()

    def get_serializer_context(self):
        ctx = super(Oauth2ECUserListView, self).get_serializer_context()
        ctx['token'] = self.token
        ctx['authentication_type'] = self.authentication_type
        return ctx

    def post(self, request, *args, **kwargs):
        # retrieve the serializer to validate data
        user_model = get_user_model()
        user_serializer = self.\
            signup_serializer_class(data=request.DATA, partial=True)
        if not user_serializer.is_valid():
            raise ParseError(user_serializer.errors)
        # user = user_serializer.create(user_serializer.validated_data)
        with transaction.atomic():
            # account name must be unique
            # at the moment account name is the same of email
            (username_fieldname, password_fieldname, 
             status_field, active_status_value,
             facebook_user_id_fieldname) = get_base_field_user_model(
                user_model
            )
            filt = {username_fieldname: user_serializer._validated_data}
            if user_model.objects.filter(**filt).exists():
                raise APIError(code='already_existent',
                               status_code=status.HTTP_400_BAD_REQUEST,
                               message='User already signed up',
                               show=True)
            # check now for authentication flow type...
            if request.DATA.get('_embedded', {}).get('facebookAuth'):
                self.authentication_type = 'facebook'
                facebook_signup_data, msg = facebook_authentication(
                    request.DATA['_embedded']['facebookAuth']
                )
                if not facebook_signup_data:
                    raise APIError(status_code=400,
                                   message='Facebook authentication failed')
                if facebook_user_id_fieldname:
                    user_serializer.\
                        validated_data[facebook_user_id_fieldname] =\
                        facebook_signup_data['id']
                user_serializer.validated_data[password_fieldname] =\
                    uuid.uuid4()
                try:
                    client_id =\
                        request.DATA['_embedded']['facebookAuth']['clientId']
                except KeyError:
                    raise APIError(code='unauthorized_client',
                                   status_code=status.HTTP_400_BAD_REQUEST,
                                   message='Missing client id')
            else:
                self.authentication_type = 'oauth'
                try:
                    client_id = request.DATA['clientId']
                except KeyError:
                    raise APIError(code='unauthorized_client',
                                   status_code=status.HTTP_400_BAD_REQUEST,
                                   message='Missing client id')
            try:
                oauth_client = Client.objects.get(client_id=client_id)
            except Client.DoesNotExist:
                logger.warning(u'bad oauth client {}'.format(client_id))
                raise APIError(code='unauthorized',
                               status_code=status.HTTP_401_UNAUTHORIZED,
                               message='OAuth client not authorized')
            user = user_serializer.create(user_serializer.validated_data)
            # set status only if defined in user model
            if status_field != '' and active_status_value != '':
                setattr(user_model, status_field, active_status_value)
            # password field is required
            # if no password is defined a system error MUST return!!!
            user.set_password(
                user_serializer.validated_data[password_fieldname]
            )
            user.save()

            # user is signed up, give him the token
            self.token = create_token(user=user, client=oauth_client)
            response_data = self.get_serializer(instance=user).data
            # add token to response for oauth2 authentication
            # TODO: embed this info into serializer

        return Response(response_data,
                        status=status.HTTP_201_CREATED)

class Oauth2ECUserView(GenericAPIView):

    serializer_class = ECUserSerializer
    # permissions will be handled on specific views

    def get_queryset(self):
        return get_user_model().objects.all()

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        user_serializer = self.get_serializer(instance=user)
        return Response(user_serializer.data,
                        status=200)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.DATA
        with transaction.atomic():
            user_serializer = self.get_serializer(instance=user, data=data,
                                                  partial=True)
            if not user_serializer.is_valid():
                raise APIError(status_code=400,
                               message=user_serializer.errors,
                               show=True)
            user_serializer.save()
            return Response(status=200,
                            data=user_serializer.data)

class Oauth2ECUserLoginView(GenericAPIView):

    serializer_class = ECUserSignupSerializer
    permission_classes = (permissions.AllowAny,)
    token = {}
    authentication_type = ''

    def get_serializer_context(self):
        ctx = super(Oauth2ECUserLoginView, self).get_serializer_context()
        ctx['token'] = self.token
        return ctx

    def post(self, request, *args, **kwargs):
        user_model = get_user_model()
        (username_fieldname, password_fieldname, 
         status_field, active_status_value,
         facebook_user_id_fieldname) = get_base_field_user_model(
            user_model
        )
        client_id = request.DATA['clientId']
        facebook_auth_data = None
        if request.DATA['grantType'] == 'facebook':
            facebook_auth_data, msg = facebook_authentication(
                request.DATA['facebookAccessToken'],
                request.DATA['facebookUserId']
            )
            if not facebook_auth_data:
                raise APIError(status_code=400,
                               message=_('facebook authentication failed'))
        else:
            # username and password are not required for facebook authentication
            username = request.DATA.get(username_fieldname, None)
            password = request.DATA.get(password_fieldname, None)
        # chech for client_id for oauth authentication
        try:
            client = Client.objects.get(client_id=client_id)
        except:
            raise APIError(code='client_unauthorized',
                           status_code=404,
                           message=_('unauthorized client'),
                           show=True)
        if facebook_auth_data:
            # use email as username if facebook auth
            username = facebook_auth_data.get('email')
            if not username:
                raise APIError(status_code=400,
                               message=_('no grant for facebook email'),
                               show=True)
        # check if user is signed up
        try:
            filt = {username_fieldname: username}
            user = user_model.objects.get(**filt)
        except user_model.DoesNotExist:
            # if no authentication with facebook then raise user not found!
            if not facebook_auth_data:
                raise APIError(code='not_found',
                               status_code=404,
                               message=_('user not found'),
                               show=True)
            else:
                user = None
        if not user:
            # facebook authentication required!
            user_serializer = self.get_serializer(data=filt,
                                                  partial=True)
            if not user_serializer.is_valid():
                raise APIError(status_code=400,
                               message=user_serializer.errors)
            if facebook_user_id_fieldname:
                user_serializer.\
                    validated_data[facebook_user_id_fieldname] =\
                    facebook_auth_data['id']
            user_serializer.validated_data[password_fieldname] =\
                uuid.uuid4()
            user = user_serializer.create(user_serializer.validated_data)
            # set status only if defined in user model
            if status_field != '' and active_status_value != '':
                setattr(user_model, status_field, active_status_value)
            # password field is required
            # if no password is defined a system error MUST return!!!
            user.set_password(
                user_serializer.validated_data[password_fieldname]
            )
            user.save()
        else:
            # the user was already created on login
            # then check if facebook authentication flow
            if facebook_auth_data:
                facebook_user_id_fieldname = getattr(
                    user_model, 'FACEBOOK_USER_ID_FIELD', None
                )
                if not facebook_user_id_fieldname:
                    raise APIError(status_code=400,
                                   message=_('Could not verify facebook auth'))
                facebook_user_id = getattr(
                    user, facebook_user_id_fieldname, None
                )
                if facebook_user_id != facebook_auth_data['id']:
                    raise APIError(status_code=400,
                                   message=_('facebook authentication failed'))
            # otherwise check if password is ok (oauth authentication)
            elif not user.check_password(password):
                raise APIError(code='wrong_password',
                               status_code=400,
                               message=_('wrong password'),
                               show=True)
        # all, ok we can authenticate this user!!! :-)
        self.request.user = user
        self.token = create_token(client=client, user=user)
        user_data = self.get_serializer(instance=user).data
        data = {'accessToken': self.token.token,
                'embedded': {'user': user_data}}
        return Response(data, status=200)

    def delete(self, request, *args, **kwargs):
        # logout user
        token = get_token_from_request(request)
        try:
            AccessToken.objects.get(token=token).delete()
        except:
            pass
        return Response(status=204)
