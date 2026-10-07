"""Validación de tipo y período para el registro actual."""
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime

from nurus.rus.columns import normalize


def earliest(today):
    month=today.year*12+today.month-1-4
    year,zero=divmod(month,12)
    return date(year,zero+1,min(today.day,monthrange(year,zero+1)[1]))


def validate_period(start,end,today=None):
    today=today or date.today()
    if not isinstance(start,date) or not isinstance(end,date) or start>end or end>today or start<earliest(today):
        raise ValueError('Las bitácoras admiten hasta los últimos cuatro meses calendario, sin fechas futuras.')


def cc_for_type(kind):
    key=normalize(kind)
    if key==normalize('Al Tribunal'):return 1
    if key==normalize('Administrativa'):return 0
    return None
