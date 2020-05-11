from django.core.exceptions import ValidationError

def mobile_validator(value):
    try:
        int(value)
    except:
        raise ValidationError('You can only enter numerals in the mobile field.')
    
    if len(value) < 10:
        raise ValidationError("Mobile numbers have to be 10 digits long.")


def number_validator(value):
    try:
        int(value)
    except:
        raise ValidationError('You can only enter numerals in this field.')
    