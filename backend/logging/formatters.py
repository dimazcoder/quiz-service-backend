import logging
import logging.config
from datetime import datetime

import pytz
from django.conf import settings

tz = pytz.timezone(settings.TIME_ZONE)

class MainFormatter(logging.Formatter):
    """ Конвертирует время в логе с учетом временной зоны django проекта """
    converter = lambda *args: datetime.now(tz).timetuple()
    