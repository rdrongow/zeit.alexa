from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import requests


app = Flask(__name__,)
ask = Ask(app, "/news")

LAST_INTENT = 'last_intent'
UNIQUE_ID = 'uniqueId'


def get_lead_story():
    req = requests.get('http://{}/lead-story'.format(
        app.settings['talk_service']))
    json = req.json()
    statement = {
        "text": u'{}: {}'.format(json['title'], json['text']),
        UNIQUE_ID: json[UNIQUE_ID]}
    return statement


def read_story(unique_id):
    req = requests.get('http://{}/read-story'.format(
        app.settings['talk_service']), params={'uniqueId': unique_id})
    return req.json()


@ask.launch
def start_skill():
    welcome_text = render_template('welcome')
    welcome_reprompt = render_template('welcome_reprompt')
    return question(welcome_text).reprompt(welcome_reprompt)


@ask.intent("LeadStoryIntent")
def lead_story():
    lead = get_lead_story()
    msg = u'Der Aufmacher ist: {} Soll ich ihn vorlesen?'.format(lead["text"])
    #msg = u'Der Aufmacher ist: {} Soll ich ihn vorlesen?'.format('Test')
    session.attributes[LAST_INTENT] = "lead_story"
    session.attributes[UNIQUE_ID] = lead[UNIQUE_ID]
    return question(msg)


@ask.intent("AMAZON.YesIntent")
def yes():
    if session.attributes.get(LAST_INTENT, False) == 'lead_story':
        return statement(read_story(session.attributes[UNIQUE_ID])['ssml'])


@ask.intent("AMAZON.NoIntent")
def no():
    return statement("OK! Bis bald.")


@ask.intent("NextStoryIntent")
def next_story():
    return statement('not implemented')


@ask.intent("AudioIntent")
def audio():
    return statement('not implemented')


@ask.intent("BreakingNewsIntent")
def breaking_news():
    return statement("")


@ask.intent("AMAZON.StopIntent")
def stop():
    return ''


@ask.intent("AMAZON.CancelIntent")
def cancel():
    return ''


@ask.intent("AMAZON.HelpIntent")
def help():
    return ''


def run(global_config, **settings):
    app.settings = settings
    return app


factory = run
