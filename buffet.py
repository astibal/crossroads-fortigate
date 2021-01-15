import os
import random
import string
import json
import urllib

from flask import Flask, request, redirect, session, url_for
from flask import make_response
from flask.json import jsonify

import config.fortigate as fortigate
import config.secrets as secrets

from string import Template
import base64

import requests


class Buffet:
    def __init__(self):
        self.cfg_fortigate = fortigate.config()


routing = Buffet()
app = Flask(__name__)
app.secret_key = secrets.config()["sessions_key"]
if secrets.config()["insecure"]:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@app.route("/error", methods=['GET'])
def error():
    return "Yikes, something bad happened."


@app.route("/ok", methods=['GET'])
def ok():
    return "OK!"

# Receive POST in form:
# 'info' -> whatever we got from upstream (ie via OAUTH userinfo)
# 'args' -> GET parameters from Fortigate
#
#   --> we want to return to upstream result JSON:
#
# 'redirect_url' -> where user should be redirected
# 'redirect_code' -> custom code
# 'redirect_data_info' -> compiled data from parametes (good for debug, can be empty)
# 'redirect_method' -> raw: decode base64 and just send it to client
#                      ...
# 'raw' (only for raw method) -> base64 blob to decode and send
@app.route('/input', methods=['POST'])
def input():
    try:

        # generate random password for Fortigate -
        #  it is needed, because fortigate, upon receiving form data with user/password triggers normal authentication
        tmp_user_pw = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(12))

        # convert to upstream data to json
        package = json.loads(request.json)

        # FIXME - use email as username -- most common, should be configurable
        username = package['info']['email']

        # extract data from Fortigate
        args = package['args']

        # start filling data_info struct
        data = {
            "username": username,
            "password": tmp_user_pw,
        }

        # safe magic value / don't crash on offline tests
        if "magic" in args.keys():
            data['magic'] = args['magic']
        else:
            data['magic'] = '1234567890'

        #
        # to_post = urllib.parse.urlencode(data)

        # construct Fortigate authd URL
        fortigate_uri = \
            routing.cfg_fortigate['fortigate_proto'] + "://" + routing.cfg_fortigate['fortigate_host'] \
            + ":" + routing.cfg_fortigate['fortigate_port'] + "/fgtauth"

        # constuct smart-ass hidden form with auto-submit feature
        magic_form = Template("""
        <div id="form-hideit">
            <form name="login" method=POST action="$url">
                <input type=hidden name="magic" value="$magic"/>
                <input type=hidden name="password" value="$pwd"/>
                <input type=text name="username" value="$user"/>
            </form>
        </div>
        <script>
        document.getElementById('form-hideit').style.display = 'none';
        window.onload = function() { document.forms["login"].submit(); };
        </script>
        """)

        # fill the form with user info data
        magic_form_body = magic_form.substitute(
                url=fortigate_uri, magic=data['magic'], pwd=tmp_user_pw, user=data['username'])
        magic_form_body = base64.b64encode(magic_form_body.encode(encoding='utf8'))

        # send our regards to upstream - form should be sent to user's
        # browser, which will send this form as the response to Fortigate captive portal

        # Note: User identifier can be whatever and password is temporary/random (we used email as it's common).
        #     You need to have some promiscuous RADIUS server to respond FortiGate.
        #
        # I used in my case (solely for testing purposes) my [raok](https://github.com/astibal/raok)
        #       testing RADIUS server. You can also pip it : `pip install raok`

        return make_response(jsonify(
            {
                "redirect_url": fortigate_uri,
                "redirect_method": "raw",
                "redirect_code": 200,
                "redirect_data_info": data,
                "raw": magic_form_body,
            }
        ))

    except KeyError as e:
        print(str(e))
        return redirect("/error")


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=6000)
