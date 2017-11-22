# -*- coding: utf-8 -*-

from StringIO import StringIO
import zeit.alexa.skill
import waitress
import logging
import threading
import pytest

log = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def app_settings(mockserver):
    return {
    }


@pytest.fixture(scope='session')
def testserver(request):
    wsgi_app = zeit.alexa.skill.factory(None)
    wsgi_app.config['ASK_VERIFY_REQUESTS'] = False
    server = waitress.server.create_server(wsgi_app, host='localhost', port=0)
    server.url = 'http://localhost:{port}'.format(port=server.effective_port)
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()

    def tearDown():
        server.task_dispatcher.shutdown()
        thread.join(5)
    request.addfinalizer(tearDown)
    return server
