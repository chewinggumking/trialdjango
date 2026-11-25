import re
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


STANDARD_INDIAN_REG_RE = re.compile(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{1,4}$')
BH_INDIAN_REG_RE = re.compile(r'^[0-9]{2}BH[0-9]{4}[A-HJ-NP-Z]{1,2}$')


def indian_vehicle_reg_validator(value):
    """Validate Indian vehicle registration numbers (standard RTO or BH series)."""
    if not value:
        return
    normalized = re.sub(r'[\s-]+', '', value.strip().upper())
    if not (STANDARD_INDIAN_REG_RE.match(normalized) or BH_INDIAN_REG_RE.match(normalized)):
        raise ValidationError(
            'Enter a valid Indian vehicle registration number (e.g. MH 02 AB 1234 or 22 BH 1234 AB).'
        )

    