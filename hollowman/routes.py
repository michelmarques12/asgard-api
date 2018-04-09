import json
import requests
from flask import url_for, redirect, Response, request, session, \
                  render_template, make_response

from hollowman.app import application
from hollowman.auth import _get_user_by_email
from hollowman.auth.google import google_oauth2
from hollowman.decorators import auth_required

from hollowman.log import logger
from hollowman.auth.jwt import jwt_auth, jwt_generate_user_info
from hollowman.plugins import get_plugin_registry_data
from hollowman import conf, request_handlers, upstream, http_wrappers


def raw_proxy():
    r = upstream.replay_request(request)
    return Response(response=r.content, status=r.status_code, headers=dict(r.headers))

@application.route("/v2/deployments", defaults={"uuid": ""}, methods=["GET"])
@application.route("/v2/deployments/<string:uuid>", methods=["GET", "DELETE"])
@auth_required()
def deployments(uuid):
    return request_handlers.Deployments(request).handle()

@application.route("/v2/groups", defaults={"group_id": ""}, methods=["GET", "DELETE"])
@application.route("/v2/groups//<path:group>/versions", methods=["GET"])
@application.route("/v2/groups/<path:group>/versions", methods=["GET"])
@application.route("/v2/groups/versions", defaults={"group": ""}, methods=["GET"])
@application.route("/v2/groups//<path:group>", methods=["GET", "PUT", "DELETE"])
@application.route("/v2/groups/<path:group>", methods=["GET", "PUT", "DELETE"])
@auth_required()
def groups(*args, **kwargs):
    return request_handlers.new(http_wrappers.Request(request))

@application.route("/v2/tasks", methods=["GET"])
@application.route("/v2/tasks/delete", methods=["POST"])
@auth_required()
def tasks():
    return request_handlers.new(http_wrappers.Request(request))

@application.route("/v2/artifacts", methods=["GET"])
@application.route("/v2/artifacts/<path:path>", methods=["GET", "PUT", "POST", "DELETE"])
@application.route("/v2/artifacts//<path:path>", methods=["GET", "PUT", "POST", "DELETE"])
@auth_required()
def artifacts(*args, **kwargs):
    return raw_proxy()

@application.route("/v2/info", methods=["GET"])
@auth_required()
def info(*args, **kwargs):
    return raw_proxy()

@application.route("/v2/leader", methods=["GET", "DELETE"])
@auth_required()
def leader(*args, **kwargs):
    return raw_proxy()

@application.route("/v2/queue", methods=["GET"])
@application.route("/v2/queue/<path:app>/delay", methods=["GET", "DELETE"])
@application.route("/v2/queue//<path:app>/delay", methods=["GET", "DELETE"])
@auth_required()
def queue(*args, **kwargs):
    return request_handlers.new(http_wrappers.Request(request))

@application.route("/ping", methods=["GET"])
@auth_required()
def ping(*args, **kwargs):
    return raw_proxy()

@application.route("/metrics", methods=["GET"])
@auth_required()
def metrics(*args, **kwargs):
    return raw_proxy()

@application.route("/", methods=["GET"])
def index():
    return Response(status=302, headers={"Location": conf.REDIRECT_ROOTPATH_TO})

@application.route('/v2/apps', defaults={'path': '/'}, methods=["GET", "POST", "PUT", "DELETE"])
@application.route('/v2/apps/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE"])
@application.route('/v2/apps//<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
@application.route('/v2/apps/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
@auth_required()
def apiv2(path):
    return request_handlers.new(http_wrappers.Request(request))

@application.route("/healthcheck")
def healhcheck():
    headers = {"Authorization": conf.MARATHON_AUTH_HEADER}
    _r = upstream._make_request("/ping", "get", headers=headers)
    return Response(response="", status=_r.status_code)


@application.route("/login/google")
def google_login():
    logger.debug("Starting Google Login")
    callback = url_for("authorized", _external=True)
    return google_oauth2.authorize(callback=callback)


def check_authentication_successful(access_token):
    headers = {'Authorization': "OAuth {}".format(access_token)}
    response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo',
                            headers=headers)
    if response.status_code != 200:
        logger.info({
            "response": response.content,
            "status_code": response.status_code
        })
        return None
    return response.json()

@application.route("/authenticate/google")
@google_oauth2.authorized_handler
def authorized(resp):
    access_token = resp and resp.get('access_token')

    authentication_ok = check_authentication_successful(access_token)
    if not authentication_ok:
        return render_template("login-failed.html", reason="Invalid OAuth2 code")

    user = _get_user_by_email(authentication_ok["email"])
    if not user:
        return render_template("login-failed.html", reason="User not found")

    if not user.accounts:
        return render_template("login-failed.html", reason="No associated accounts")

    data = {}
    data["jwt"]: bytes = jwt_auth.jwt_encode_callback(jwt_generate_user_info(user, user.accounts[0]))

    session["jwt"] = data["jwt"] = data["jwt"].decode('utf-8')
    return redirect("{}?jwt={}".format(conf.REDIRECT_AFTER_LOGIN, data["jwt"]))


@google_oauth2.tokengetter
def get_access_token():
    return session.get('access_token')


@application.route("/v2/plugins")
def plugins():
    return make_response(json.dumps(get_plugin_registry_data()), 200)


@application.route("/v2/plugins/<string:plugin_id>/main.js")
def main_js(plugin_id):
    return redirect("static/plugins/{}/main.js".format(plugin_id))

