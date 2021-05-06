from datetime import datetime

from django.utils.deprecation import MiddlewareMixin


class TimeToLater(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_staff:
            work = request.session.get('work', False)
            if work:
                if work < datetime.timestamp(datetime.now()) - 60 * 5:
                    request.path = '/logout/'
                    request.path_info = '/logout/'
                work = datetime.timestamp(datetime.now())
                request.session['work'] = work
            else:
                work = datetime.timestamp(datetime.now())
                request.session['work'] = work
