# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import requests
import re


app = Flask(__name__,)
ask = Ask(app, "/news")

LAST_INTENT = 'last_intent'
UNIQUE_ID = 'uniqueId'


def _prepare_statement(json):
    return {
        "text": u'{}: {}'.format(json['title'], json['text']),
        UNIQUE_ID: json[UNIQUE_ID]}


def _request(action, unique_id=None):
    params = None
    if unique_id:
        params = {"uniqueId": unique_id}
    return requests.get('http://{}/{}'.format(
        app.settings['talk_service'], action), params=params).json()


def _teaser(action, unique_id=None):
    return _prepare_statement(_request(action, unique_id))


def get_lead_story():
    return _teaser('lead-story', None)


def get_next_story(unique_id):
    return _teaser('next-story', unique_id)


def get_previous_story(unique_id):
    return _teaser('previous-story', unique_id)


def read_story(unique_id):
    return _request('read-story', unique_id)


def _strip_tags(xml_str):
    p = re.compile(r'<.*?>')
    story = p.sub('', xml_str)
    story = story.replace('\n', ' ').replace('\r', ' ')
    story = re.sub(' +', ' ', story)
    return story


def maybe_chunk_story(story):
    try:
        # Cleanup chunks
        session.attributes.pop('chunk_index')
    except KeyError:
        pass

    story = _strip_tags(story)

    if len(story) <= 7500:
        return story

    # XXX: Maybe preserve SSML
    story_chunk = ''
    if len(story) >= 7500:
        story_chunk = story[7500:]
        story = story[:7500]

    if not story.endswith('.') and "." in story_chunk:
        story = "%s%s" % (story, story_chunk[:story_chunk.index(".")+1])

    if story_chunk:
        prev_index = session.attributes.pop('prev_chunk_index', 0)
        session.attributes['chunk_index'] = len(story) + prev_index
    return story


def story_from_session():
    if ('chunk_index' in session.attributes.keys() and
            UNIQUE_ID in session.attributes.keys()):
        index = session.attributes.pop('chunk_index')
        story = _strip_tags(read_story(session.attributes[UNIQUE_ID])['ssml'])
        story = story[index:]
        session.attributes['prev_chunk_index'] = index
        return story


def is_story_chunked():
    return 'chunk_index' in session.attributes.keys()


@ask.launch
def start_skill():
    welcome_text = render_template('welcome')
    welcome_reprompt = render_template('welcome_reprompt')
    return question(welcome_text).reprompt(welcome_reprompt)


@ask.intent("LeadStoryIntent")
def lead_story():
    lead = get_lead_story()
    msg = u'Der Aufmacher ist: {} Soll ich ihn vorlesen?'.format(lead["text"])
    session.attributes[LAST_INTENT] = "lead_story"
    session.attributes[UNIQUE_ID] = lead[UNIQUE_ID]
    return question(msg)


def read_any_story():
    unique_id = session.attributes.get(UNIQUE_ID, None)
    if not unique_id:
        story = get_lead_story()
        unique_id = story[UNIQUE_ID]
    read = maybe_chunk_story(read_story(unique_id)['ssml'])
    session.attributes[UNIQUE_ID] = unique_id
    action = statement
    if is_story_chunked():
        action = question
        read = "%s Weiterlesen? Sagen Sie weiter!" % (read)
    return action(read)


@ask.intent("ReadLeadStoryIntent")
def read_lead_story():
    session.attributes.pop(UNIQUE_ID, None)
    return read_any_story()


@ask.intent("ContinueReadingIntent")
def continue_reading():
    if not is_story_chunked():
        session.attributes[LAST_INTENT] = 'continue_reading'
        return question(u"Es gibt gerade keinen Artikel, den ich weiterlesen "
                        u"könnte. Soll ich den ersten Artikel der Homepage "
                        u"vorlesen?")

    read = maybe_chunk_story(story_from_session())
    action = statement
    if is_story_chunked():
        action = question
        read = "%s Weiterlesen? Sagen Sie weiter!" % (read)
    return action(read)


@ask.intent("AMAZON.YesIntent")
def yes():
    if LAST_INTENT not in session.attributes.keys():
        session.attributes[LAST_INTENT] = 'yes'
        return question(
            "Ich weiss nicht was Sie meinen. "
            "Soll ich den Leitartikel vorlesen?")
    if session.attributes[LAST_INTENT] == 'lead_story':
        return read_lead_story()
    if (session.attributes[LAST_INTENT] == 'next_story' or
            session.attributes[LAST_INTENT] == 'previous_story'):
        return read_any_story()
    if session.attributes[LAST_INTENT] == 'continue_reading' or (
       session.attributes[LAST_INTENT] == 'yes'):
        return read_lead_story()


@ask.intent("AMAZON.NoIntent")
def no():
    return statement("OK! Bis bald.")


@ask.intent("NextStoryIntent")
def next_story():
    story = get_next_story(session.attributes[UNIQUE_ID])
    msg = u'Nächster Artikel: {} Soll ich ihn vorlesen?'.format(story["text"])
    session.attributes[LAST_INTENT] = "next_story"
    session.attributes[UNIQUE_ID] = story[UNIQUE_ID]
    return question(msg)


@ask.intent("PreviousStoryIntent")
def previous_story():
    story = get_previous_story(session.attributes[UNIQUE_ID])
    msg = u'Voriger Artikel: {} Soll ich ihn vorlesen?'.format(story["text"])
    session.attributes[LAST_INTENT] = "previous_story"
    session.attributes[UNIQUE_ID] = story[UNIQUE_ID]
    return question(msg)


@ask.intent("AudioIntent")
def audio():
    return statement('not implemented')


@ask.intent("BreakingNewsIntent")
def breaking_news():
    return statement("")


@ask.intent("AMAZON.StopIntent")
def stop():
    return statement('Auf bald.')


@ask.intent("AMAZON.CancelIntent")
def cancel():
    return statement('OK!')


@ask.intent("AMAZON.HelpIntent")
def help():
    return statement("Hilfe!")


def run(global_config, **settings):
    app.settings = settings
    return app


factory = run
