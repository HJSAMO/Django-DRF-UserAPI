import re

from django.core.exceptions import ValidationError


def validate_email(email):
    if re.match('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) is None:
        raise ValidationError('Invalid email.')
