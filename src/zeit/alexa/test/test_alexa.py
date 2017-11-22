# -*- coding: utf-8 -*-
from requests import post
import copy


base_request = {
  "version": "1.0",
  "session": {
    "new": True,
    "sessionId": "amzn1.echo-api.session.0000000-0000-0000-0000-00000000000",
    "application": {
      "applicationId": "fake-application-id"
    },
    "attributes": {},
    "user": {
      "userId": "amzn1.account.AM3B00000000000000000000000"
    }
  },
  "context": {
    "System": {
      "application": {
        "applicationId": "fake-application-id"
      },
      "user": {
        "userId": "amzn1.account.AM3B00000000000000000000000"
      },
      "device": {
        "supportedInterfaces": {
          "AudioPlayer": {}
        }
      }
    },
    "AudioPlayer": {
      "offsetInMilliseconds": 0,
      "playerActivity": "IDLE"
    }
  }
}


def _client(request_data):
    request = copy.deepcopy(base_request)
    request['request'] = request_data
    return request


def _get_text(http_response):
        data = http_response.json()
        return data.get('response', {})\
                   .get('outputSpeech', {})\
                   .get('text', None)


def _get_reprompt(http_response):
        data = http_response.json()
        return data.get('response', {})\
                   .get('reprompt', {})\
                   .get('outputSpeech', {})\
                   .get('text', None)


def test_launch_app(testserver):
    request = _client({
        "type": "LaunchRequest",
        "requestId": "string",
        "timestamp": "string",
        "locale": "string",
        "intent": {
            "name": "TestPlay",
            "slots": {}
        }
    })
    response = post('{}/{}'.format(
        testserver.url, 'news'), json=request)

    assert response.ok

    assert _get_text(response) == (
        'Willst du die News wissen?')

    assert _get_reprompt(response) == (
        'Sage ja oder nein, wenn du die News wissen willst.')


def test_yes_intent(testserver):
    request = _client({
        "type": "IntentRequest",
        "intent": {
            "name": "YesIntent",
            "slots": {}
        }
    })
    response = post('{}/{}'.format(
        testserver.url, 'news'), json=request)

    assert response.ok

    assert _get_text(response) == (
        'Die aktuelle...Test headline')
