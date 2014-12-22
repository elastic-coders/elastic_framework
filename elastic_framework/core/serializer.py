''' extension of DRF serializer

'''

from rest_framework.fields import ChoiceField
from rest_framework.exceptions import ValidationError


class DisplayFieldWithChoice(ChoiceField):
    ''' Used into serializer to display choiced field
    This field has a model mapping so you can define it as writable too

    '''

    def __init__(self, choices=(), *args, **kwargs):
        super(DisplayFieldWithChoice, self).\
            __init__(choices=choices, *args, **kwargs)
        # prepare dictionary with direct and reverted choices
        self.revert = {
            value: key for key, value in self.choices.items()
        }
        self.forward = {
            key: value for key, value in self.choices.items()
        }

    def valid_value(self, value):
        return value in self.forward

    def run_validation(self, value):
        try:
            return self.revert.get(value)
        except KeyError:
            raise ValidationError('{}: invalid value for choice field'.\
                                      format(value))

    def to_representation(self, value):
        return self.forward.get(value)
