from django.http.response import JsonResponse as JSR
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from portal.models import notify_devs

@csrf_exempt
def respond(request):
    notify_devs('warning',request.body)
    try:
        body = json.loads(request.body)
    except TypeError:
        body = json.loads(str((request.body.decode('utf-8'))))
    if 'challenge' in body:
        challenge_val = body['challenge']
        notify_devs('warning', 'body is: {} and challenge is: {}'.format(str(body), challenge_val))
        return HttpResponse(content=json.dumps({'challenge':challenge_val}), content_type='application/json')
