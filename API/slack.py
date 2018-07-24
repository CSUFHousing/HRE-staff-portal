from django.http.response import JsonResponse as JSR
from django.http.response import HttpResponse
import json

from portal.models import notify_devs

def challenge(request, body):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

def respond(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    if 'challenge' in body:
        challenge_val = body['challenge']
        notify_devs('warning', 'body is: {} and challenge is: {}'.format(str(body), challenge_val))
        return HTTPResponse(content='challenge_val', content_type='text/plain')
