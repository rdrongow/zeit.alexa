from flask import Flask
from flask_ask import Ask, statement, question, session


app = Flask(__name__,)
ask = Ask(app, "/news")


def get_headlines():
    return 'Test headline'


@ask.launch
def start_skill():
    welcome_message = 'Willst du die News wissen?'
    return question(welcome_message).reprompt(
        'Sage ja oder nein, wenn du die News wissen willst.')


@ask.intent("YesIntent")
def share_headlines():
    headlines = get_headlines()
    headline_msg = 'Die aktuellen Schlagzeilen sind: {}'.format(headlines)
    return statement(headline_msg)


@ask.intent("NoIntent")
def no_intent():
    bye_text = 'OK! Auf Wiedersehen!'
    return statement(bye_text)


def run(global_config, **settings):
    app.settings = settings
    return app


factory = run
