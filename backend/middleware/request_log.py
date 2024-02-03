import json
import logging
import time
import traceback
from typing import Tuple

from django.conf import settings
from django.http import JsonResponse
from rest_framework.status import (HTTP_400_BAD_REQUEST,
                                   HTTP_500_INTERNAL_SERVER_ERROR)

request_logger = logging.getLogger(__name__)

class RequestLogMiddleware:
    """Middleware для логгирования запросов и ответов API"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        log_message, log_data = self.prepare_log_data_for_request(request=request)

        response = self.get_response(request)

        # if not isinstance(response, Exception):
        status_code = getattr(response, 'status_code', None)
        log_message += f' {status_code}'
    
        if response and 'content-type' in response and response['content-type'] == 'application/json':
            response_body = json.loads(response.content.decode('utf-8'))
            log_data['response_body'] = json.dumps(response_body, indent=4, ensure_ascii=False)
            
        log_data['run_time'] = time.monotonic() - start_time

        log_record = '{}\r\n{}'.format(
            log_message,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in log_data.items()),
        )

        if status_code >= HTTP_400_BAD_REQUEST:
            request_logger.warning(log_record)
        else:
            request_logger.info(log_record)

        return response

    def prepare_log_data_for_request(self, request) ->Tuple[str, dict]:
        """ Подготавливает сообщение для записи в лог по данным в реквесте """
        log_message = f'"{request.method} {request.get_full_path()} {request.META["SERVER_PROTOCOL"]}"'
        log_data = {}
        
        if 'HTTP_USER_AGENT' in request.META:
          log_data['user_agent'] = request.META['HTTP_USER_AGENT']

        if 'REMOTE_ADDR' in request.META:
          log_data['remote_address'] = request.META['REMOTE_ADDR']

        # log_data = {
        #     'user_agent': request.META['HTTP_USER_AGENT'],
        #     'remote_address': request.META['REMOTE_ADDR'],
        # }

        if request.body:
            # Обработаю и json-параметры, и post-парамтеры
            request_body = json.loads(request.body.decode('utf-8')) if 'application/json' in request.META['CONTENT_TYPE'] else request.POST.dict()
            log_data['request_body'] = json.dumps(request_body, indent=4, ensure_ascii=False)

        return (log_message, log_data)

    def process_exception(self, request, exception):
        log_message, log_data = self.prepare_log_data_for_request(request=request)

        if exception:
            log_data['exception'] = repr(exception)
            log_data['traceback'] = traceback.format_exc()

        log_record = '{}\r\n{}'.format(
            log_message,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in log_data.items()),
        )

        request_logger.error(log_record)

        if settings.DEBUG:
            return None
        else:
            # Не показывать клиенту ошибку (возможно Django сам скрывает и это не нужно будет на проде)
            return JsonResponse({'message': 'Упс! Что-то пошло не так...'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
