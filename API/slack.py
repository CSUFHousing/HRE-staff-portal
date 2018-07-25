from django.http.response import JsonResponse as JSR
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

from portal.models import notify_devs

@csrf_exempt
def respond(request):
    notify_devs('warning',request.body)
    body = json.loads(request.body)
    if 'challenge' in body:
        challenge_val = body['challenge']
        notify_devs('warning', 'body is: {} and challenge is: {}'.format(str(body), challenge_val))
        return HttpResponse(content=challenge_val, content_type='application/json')
