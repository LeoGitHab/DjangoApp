import time

from django.http import HttpRequest


def set_useragent_on_request_middleware(get_response):
    print('Initial call')

    def middleware(request: HttpRequest):
        print('Before get_response')
        request.user_agent = request.META['HTTP_USER_AGENT']
        response = get_response(request)
        print('After get_response')
        return response

    return middleware


class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0
        # self.requests_time = {}

    def __call__(self, request: HttpRequest):
        # time_delay = 1
        # if not self.requests_time:
        #     print('This is a first request after server restart, dict is empty.')
        # else:
        #     if (round(time.time()) * 1) - self.requests_time['time'] < time_delay \
        #             and self.requests_time['ip_address'] == request.META.get('REMOTE_ADDR'):
        #         print(f'Time between two requests is less then {time_delay} from your IP-address!')
        #         return render(request, 'requestdataapp/error-request.html')
        #
        # self.requests_time = {'time': round(time.time()) * 1, 'ip_address': request.META.get('REMOTE_ADDR')}

        self.requests_count += 1
        print('requests_count =', self.requests_count)
        response = self.get_response(request)
        self.responses_count += 1
        print('responses_count =', self.responses_count)
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print('exceptions_count =', self.exceptions_count)




