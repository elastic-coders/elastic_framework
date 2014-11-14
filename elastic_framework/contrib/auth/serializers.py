from django.contrib.auth import get_user_model

from rest_framework import serializers


class ECUserSignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()

    def to_native(self, obj):
        return super(ECUserSignupSerializer, self).to_native(obj)

    '''
    def __init__(self, instance=None, data=None, **kwargs):
        if data:
            if 'email' not in data:
                data['email'] = ''
            else:
            attrs['email'] = self.Meta.model.objects.\
            normalize_email(attrs['email']).lower()
        # if none for the moment set account_name equal to email
            if data.get('account_name', None) in [None, '']:
                data['account_name'] = data['email']
        return super(ECUserSignupSerializer, self).\
            __init__(instance, data, **kwargs)
            '''

    def to_python(self):
        pass
    

class ECUserResponseSerializerClass(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()

    @property
    def data(self):
        data = super(ECUserResponseSerializerClass, self).data
        if not self.context or not self.context.get('token', None):
            raise ValueError('token field required in context from view')
        data['_embedded'] = {}
        data['_embedded']['oauth'] = {'access_token': self.\
                                          context['token'].token,
                                      'grant_type': 'password'}
        return data
