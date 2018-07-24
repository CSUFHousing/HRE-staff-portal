from django.http.response import JsonResponse as JSR
from django.http.response import HttpResponse
import json

from portal.models import notify_devs

def respond(request):
    body = json.loads(request.body)
    if 'challenge' in body:
        challenge_val = body['challenge']
        notify_devs('warning', 'body is: {} and challenge is: {}'.format(str(body), challenge_val))
        return HTTPResponse(content='challenge_val', content_type='text/plain')
