import logging
import requests
import json
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session, context, request

app = Flask(__name__)
ask = Ask(app, "/")
logger = logging.getLogger("flask_ask")
logger.setLevel(logging.DEBUG)

PASTAS = ["esperimento", "mezzanotte"]

def issue_progressive_response(speech):
    """
    Send the user an upfront response via the directives API, to distract them whilst we perform a slow operation and
    generate a response
    :returns Future, call .result() to force it to complete
    """
    url = '{}/v1/directives'.format(context.System.apiEndpoint)
    token = context.System.apiAccessToken
    request_id = request.requestId
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(token)
    }
    body = {
        'header': {'requestId': request_id},
        'directive': {'type': 'VoicePlayer.Speak', 'speech': speech}
    }
    return requests.post(url, headers=headers, json=body)

@ask.launch
def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)

@ask.intent("RandomPasta")
def read_pasta():
    pasta = randint(0, len(PASTAS)-1)
    pasta_msg = render_template(PASTAS[pasta])
    if len(pasta_msg) > 8000:
        
        #Progressive responses
        latest = 0
        for i in range(600, 8000, 600):
            sliced = pasta_msg[i-600:i]
            logger.info(sliced)
            issue_progressive_response(sliced)
        issue_progressive_response(pasta_msg[latest:8000])

        return statement(pasta_msg[8001:])
    else:
        return statement(pasta_msg)


if __name__ == '__main__':
    app.run(debug=True)