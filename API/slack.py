from django.http import JsonResponse as JSR
from django.http import HTTPResponse
import json

from portal.models import notify_devs

def challenge(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    challenge_val = body['challenge']
    notify_devs('warning', 'body is: {} and challenge is: {}'.format(str(body), challenge_val))
    return HTTPResponse(content='challenge_val', content_type='text/plain')
