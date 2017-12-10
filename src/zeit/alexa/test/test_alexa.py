# -*- coding: utf-8 -*-
from requests import post
import zeit.alexa.skill
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


def _get_text(http_response, mode):
        data = http_response.json()
        return data.get('response', {})\
                   .get('outputSpeech', {})\
                   .get(mode, None)


def _get_reprompt(http_response, mode):
        data = http_response.json()
        return data.get('response', {})\
                   .get('reprompt', {})\
                   .get('outputSpeech', {})\
                   .get(mode, None)


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

    assert _get_text(response, 'ssml') == (
        '')

    assert _get_reprompt(response, 'ssml') == (
        'Sage ja oder nein, wenn du die News wissen willst.')


def test_lead_story_intent(testserver, monkeypatch):
    request = _client({
        "type": "IntentRequest",
        "intent": {
            "name": "lead_story",
            "slots": {}
        }
    })

    def lead():
        return 'Meine Titel: Meine Unterzeile'

    monkeypatch.setattr(zeit.alexa.skill, 'get_lead_story', lead)
    response = post('{}/{}'.format(
        testserver.url, 'news'), json=request)

    assert response.ok

    assert _get_text(response, 'text') == (
        'Der Aufmacher ist: Meine Titel: Meine Unterzeile')
