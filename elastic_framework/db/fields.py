''' Here we define all fields type


'''

from __future__ import absolute_import

from django.db import models
from south.modelsinspector import add_introspection_rules


class CountryField(models.CharField):

    # XXX TODO: define the list of value for CountrField...
    # same value must be used for LanguageField
    def __init__(self, name=None, **kwargs):
        field_params = {'max_length': 2, 'blank': True, 'null': True}
        field_params.update(kwargs)
        super(CountryField, self).__init__(name=name, **field_params)

class CurrencyField(models.CharField):

    # XXX TODO: define the list of value for CurrencyField...
    def __init__(self, name=None, **kwargs):
        field_params = {'max_length': 3, 'blank': True, 'null': True}
        field_params.update(kwargs)
        super(CurrencyField, self).__init__(name=name, **field_params)


class CharListField(models.TextField):
    ''' In the model this type of field is a list of strings
    i.e. ['red', 'green', 'yellow']
    that in db is represented by 'red,green,yellow'
    
    '''
    __metaclass__ = models.SubfieldBase

    def get_prep_value(self, value):
        '''transform list of strings into comma-separeted string value'''
        if value is None:
            return None
        return u','.join(value)

    def to_python(self, value):
        ''' '''
        if value is None:
            return []
        if isinstance(value, basestring):
            return value.split(u',')
        return value


add_introspection_rules([], ["^elastic_frameworks\.db\.fields\.CountryField"])

add_introspection_rules([], ["^elastic_frameworks\.db\.fields\.CurrencyField"])

add_introspection_rules([], ["^elastic_frameworks\.db\.fields\.CharListField"])
