from django.http.response import JsonResponse as JSR
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import requests
import json

from django.conf import settings

from portal.models import notify_devs

@csrf_exempt
def respond(request):
    body = request.POST
    notify_devs("primary", body)
    if 'challenge' in body:
        challenge_val = body['challenge']
        notify_devs('warning', 'body is: {} and challenge is: {}'.format(str(body), challenge_val))
        return HttpResponse(content=json.dumps({'challenge':challenge_val}), content_type='application/json')
    elif 'payload' in body:
        payload = json.loads(body['payload'])
        channel = payload["channel"]["id"]
        response_url = payload["response_url"]
        responding_user = payload["user"]["username"]
        reaction_result = payload["actions"][0]["value"]

        notify_devs("success", "reaction received from {}: {}".format(responding_user, reaction_result))
        r = requests.post(response_url, data=json.dumps({"replace_origina":"true","text":"response received and processing"}),
                          headers = {"Content-type":"application/json"})
        return HttpResponse(content=None)


def send_to_slack(content, channel="GBWTZANG6", url="https://slack.com/api/chat.postMessage"):
    payload = json.dumps({"channel": channel, "blocks": content})
    headers = {"Content-type":"application/json", "Authorization": "Bearer {}".format(settings.SLACK_API_TOKEN)}
    print(settings.SLACK_API_TOKEN)
    return requests.post(url, data=payload, headers=headers)


def room_notify(room="Acacia-101", channel="GBWTZANG6"):
    blocks = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Acacia-102 is empty and ready for inspection."
        }
    },
   {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": ":white_check_mark: Good to go!"
                },
                "style": "primary",
                "value": "good"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": ":x: Has a problem!"
                },
                "style": "danger",
                "value": "bad"
            }
        ]
    }
]
    send_to_slack(blocks, channel)

def respond_to_slack_interaction(request):
    try:
        body = json.loads(request.body)
    except TypeError:
        body = json.loads(str((request.body.decode('utf-8'))))
