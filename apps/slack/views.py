import os

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from slackclient import SlackClient

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)
VIRAL_CONTENT = 'CAKPMLF8W'

# run the below command to stat ngrok
# ~/Downloads/ngrok http 8000
class Events(APIView):
    def post(self, request, *args, **kwargs):
        slack_message = request.data
        print(slack_message)
        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)
        # greet bot
        if 'event' in slack_message:
            event_message = slack_message.get('event')

            # ignore bot's own message
            if event_message.get('subtype') == 'bot_message':
                return Response(status=status.HTTP_200_OK)

                # process user's message
            user = event_message.get('user')
            text = event_message.get('text')
            channel = event_message.get('channel')
            bot_text = 'Hi <@{}> :wave:'.format(user)
            print('From-Slack', text)

            if 'hi' in text.lower():
                Client.api_call(method='chat.postMessage',
                                channel=channel,
                                text=bot_text)
                return Response(status=status.HTTP_200_OK)


        return Response(status=status.HTTP_200_OK)


# Create your views here.
from slackclient import SlackClient

# # slack_token = os.environ["slacktoken"]
# slack_token = "xoxb-359048301733-6jFLGaFdi2LxWyTgbWoGW985"
# sc = SlackClient(slack_token)
#
# sc.api_call(
#   "chat.postMessage",
#   channel="DA2SBAEBU",
#   text="Hello from Jonathan! :tada:",
# )

#send from slack
# {'token': '2xGss40SBb686x33MFTJdoGZ', 'team_id': 'T0R5VA1MZ', 'api_app_id': 'AAKU65YNB', 'event': {'type': 'message', 'user': 'U9TNP1U3H', 'text': 'hi', 'ts': '1525524656.000041', 'channel': 'DAJB9K02D', 'event_ts': '1525524656.000041', 'channel_type': 'im'}, 'type': 'event_callback', 'event_id': 'EvAJB9UP33', 'event_time': 1525524656, 'authed_users': ['UAK1E8VMK']}
#sent to slack
#{'token': '2xGss40SBb686x33MFTJdoGZ', 'team_id': 'T0R5VA1MZ', 'api_app_id': 'AAKU65YNB', 'event': {'text': 'Hi <@U9TNP1U3H> :wave:', 'username': 'news-aggregator', 'bot_id': 'BAJ69NSGG', 'type': 'message', 'subtype': 'bot_message', 'ts': '1525524657.000068', 'channel': 'DAJB9K02D', 'event_ts': '1525524657.000068', 'channel_type': 'im'}, 'type': 'event_callback', 'event_id': 'EvAK1YDH1B', 'event_time': 1525524657, 'authed_users': ['UAK1E8VMK']}
