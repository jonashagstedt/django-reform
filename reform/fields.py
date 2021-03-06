from django.core.urlresolvers import reverse, NoReverseMatch
from .field_validators import MaxLengthValidator, EmailValidator, URLValidator, MinValueValidator, MaxValueValidator
from django.conf import settings


class Field(object):
    field_type = 'base_field'

    def __init__(self, required=True, label=None, initial=None, help_text=None, error_messages=None, *args, **kwargs):
        self.required = required
        self.label = label
        self.initial = initial
        self.help_text = help_text
        self.error_messages = error_messages
        self.validators = []
        self.kwargs = kwargs


    def to_dict(self, **kwargs):
        validators = [validator.to_dict() for validator in self.validators]
        data = {
            'field_type': self.field_type,
            'label': self.label,
            'initial': self.initial,
            'help_text': self.help_text,
            'required': self.required,
            'error_messages': self.error_messages,
            'validators': validators
        }

        data.update(self.kwargs)
        data.update(kwargs)
        return data

    def get_value(self, post_data, name):
        if self.multi_value:
            return post_data.getlist(name)
        else:
            return post_data.get(name)

    @property
    def multi_value(self):
        return self.kwargs.get('multi') is True

    def __str__(self):
        return self.field_type

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.__str__())


class CharField(Field):
    field_type = 'char'

    def __init__(self, max_length=None, *args, **kwargs):
        super(CharField, self).__init__(*args, **kwargs)
        if max_length:
            self.validators.append(MaxLengthValidator(max_length))


class TextField(Field):
    field_type = 'text'


class EmailField(CharField):
    field_type = 'email'

    def __init__(self, max_length=255, *args, **kwargs):
        super(EmailField, self).__init__(*args, **kwargs)
        self.validators.append(EmailValidator(max_length))


class URLField(CharField):
    field_type = 'url'

    def __init__(self, max_length=2083, *args, **kwargs):
        super(URLField, self).__init__(*args, **kwargs)
        self.validators.append(URLValidator(max_length))


class BooleanField(Field):
    field_type = 'boolean'


class IntegerField(Field):
    field_type = 'integer'

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        if min_value:
            self.validators.append(MinValueValidator(min_value=min_value))
        if max_value:
            self.validators.append(MaxValueValidator(max_value=max_value))


class DecimalField(Field):
    field_type = 'decimal'

    def __init__(self, min_value=None, max_value=None, decimal_places=None, *args, **kwargs):
        super(DecimalField, self).__init__(*args, **kwargs)
        self.decimal_places = decimal_places
        if min_value:
            self.validators.append(MinValueValidator(min_value=min_value))
        if max_value:
            self.validators.append(MaxValueValidator(max_value=max_value))

    def to_dict(self, **kwargs):
        data = super(DecimalField, self).to_dict(**kwargs)
        data['decimal_places'] = self.decimal_places
        return data


class TemporalField(Field):
    def to_dict(self, **kwargs):
        data = super(TemporalField, self).to_dict(**kwargs)
        data['format'] = self.format
        return data


class DateTimeField(TemporalField):
    field_type = 'date_time'

    def __init__(self, format=None, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)
        if format is None:
            self.format = getattr(settings, 'REFORM_DATE_TIME', 'dd/mm/yyyy HH:mm')


class DateField(TemporalField):
    field_type = 'date'

    def __init__(self, format=None, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)
        if format is None:
            self.format = getattr(settings, 'REFORM_DATE', 'dd/mm/yyyy')


class TimeField(TemporalField):
    field_type = 'time'

    def __init__(self, format=None, *args, **kwargs):
        super(TimeField, self).__init__(*args, **kwargs)
        if format is None:
            self.format = getattr(settings, 'REFORM_TIME', 'HH:mm')


class ChoiceField(Field):
    field_type = 'select'

    def __init__(self, choices=None, key_field='key', label_field='label', *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self.choices = choices
        self.key_field = key_field
        self.label_field = label_field

    def to_dict(self, **kwargs):
        data = super(ChoiceField, self).to_dict(**kwargs)
        if isinstance(self.choices, str):
            try:
                choice_url = reverse(self.choices)
            except NoReverseMatch:
                choice_url = self.choices
            data['choices'] = choice_url
        else:
            data['choices'] = self.choices
            # for choice in self.choices:
            #     data['choices'].push()
            #     import ipdb;ipdb.set_trace()
        # elif isinstance(self.choices, dict):
        #     data['choices'] = [{self.key_field: k, self.label_field: v} for (k, v) in self.choices.items()]
        # else:
        #     data['choices'] = [{self.key_field: k, self.label_field: v} for (k, v) in self.choices]
        data['key_field'] = self.key_field
        data['label_field'] = self.label_field
        return data


class RadioListField(ChoiceField):
    field_type = 'radio_select'


class Button(Field):
    field_type = 'button'


fields = {
    CharField.field_type: CharField,
    TextField.field_type: TextField,
    EmailField.field_type: EmailField,
    URLField.field_type: URLField,
    BooleanField.field_type: BooleanField,
    IntegerField.field_type: IntegerField,
    DecimalField.field_type: DecimalField,
    DateTimeField.field_type: DateTimeField,
    DateField.field_type: DateField,
    TimeField.field_type: TimeField,
    ChoiceField.field_type: ChoiceField,
    RadioListField.field_type: RadioListField,
    Button.field_type: Button,
}
