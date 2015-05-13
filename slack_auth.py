# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, unicode_literals

import json
import os
import sys
from urllib.parse import urlencode
import uuid

import flask
import requests


USAGE = """\
You must set SLACK_CLIENT_ID and SLACK_CLIENT_SECRET for this to work.

If you haven't alredy, go to https://api.slack.com/applications/new
and create an app. Make sure the URL this application is running at
(usually http://127.0.0.1:5000) is listed in the "Redirect URI(s)"
field.

Then set the environment vars and re-launch.
"""

try:
    SLACK_CLIENT_ID = os.environ['SLACK_CLIENT_ID']
    SLACK_CLIENT_SECRET = os.environ['SLACK_CLIENT_SECRET']
except KeyError:
    print(USAGE)
    sys.exit(1)


SLACK_AUTHORIZE_URL = 'https://slack.com/oauth/authorize'
SLACK_OAUTH_URL = 'https://slack.com/api/oauth.access'

app = flask.Flask(__name__)


@app.route('/')
def main_view():
    if 'error' in flask.request.args:
        return 'Access was denied', 403, {'Content-type': 'text/plain'}

    if 'code' in flask.request.args:
        response = requests.get(
            SLACK_OAUTH_URL,
            params={
                'client_id': SLACK_CLIENT_ID,
                'client_secret': SLACK_CLIENT_SECRET,
                'code': flask.request.args['code'],
                'redirect_uri': flask.url_for('.main_view', _external=True),
            })
        return (json.dumps(response.json()), 200,
                {'Content-type': 'application/json'})

    redirect_url = '{}?{}'.format(
        SLACK_AUTHORIZE_URL,
        urlencode({
            'client_id': SLACK_CLIENT_ID,
            'redirect_uri': flask.url_for('.main_view', _external=True),
            'scope': 'identify,read,post,client',
            'state': str(uuid.uuid4()),
            # 'team': None,
        }))
    return flask.redirect(redirect_url)


if __name__ == '__main__':
    app.run(debug=True)
