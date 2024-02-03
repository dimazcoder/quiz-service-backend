import logging


class FilterLevels(logging.Filter):
    """ Кастомный фильтр для логгера, чтобы разделить разные уровни логов по разным файлам """
    def __init__(self, filter_levels=None):
       super(FilterLevels, self).__init__()
       self._filter_levels = filter_levels
 
    def filter(self, record):
        if record.levelname in self._filter_levels:
            return True
        return False
        