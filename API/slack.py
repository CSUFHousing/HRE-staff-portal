from django.http.response import JsonResponse as JSR
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import requests
import json

from portal.models import notify_devs

MS_FLOW_URL="https://prod-54.westus.logic.azure.com:443/workflows/306a0803a4ee49fc939bb1a1a7467829/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=LPDDdoYWwIkmlKVdgu_0PPOa5cMPHFzm8GOOyqqiSn8"

@csrf_exempt
def dispatch(request):
    body = request.POST
    room = body["room"]
    room_notify(room=room)
    return HttpResponse(content=None)

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
        # channel = payload["channel"]["id"]
        response_url = payload["response_url"]
        responding_user_id = payload["user"]["id"]
        responding_user = payload["user"]
        reaction = payload["actions"][0]["value"]
        reaction_results = reaction.split("|")
        room = reaction_results[0]
        status = reaction_results[1]

        notify_devs("success", "reaction received from {}: {}".format(responding_user, reaction_results))
        # send reaction to slack
        r1 = requests.post(response_url, data=json.dumps({"replace_original":"true","text":"<@{}> marked {} as {}.".format(
            responding_user_id, room, status)}),headers={"Content-type":"application/json"})
        # send update to MS Flow to update spreadsheet.
        ms_flow_data = {"room":room, "result":status, "userid":responding_user}
        r2 = requests.post(MS_FLOW_URL, data=json.dumps(ms_flow_data), headers={"Content-type": "application/json"})
        # update message in Slack with MS Flow response
        r3 = requests.post(response_url, data=json.dumps({"ephemeral": "true", "text": "{}".format(r2.status_code)}),
                           headers={"Content-type": "application/json"})
        notify_devs("danger","process finished\n{}-{}\n{}-{}".format(r2.status_code, r2.text, r3.status_code, r3.text))
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
            "text": "{} is empty and ready for inspection.".format(room)
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
                "value": "{}|good".format(room)
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": ":x: Has a problem!"
                },
                "style": "danger",
                "value": "{}|bad".format(room)
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
