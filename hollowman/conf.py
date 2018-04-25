import os
import base64

from marathon import MarathonClient
from asgard.sdk.options import get_option

ENABLED = "1"
DISABLED = "0"

MARATHON_CREDENTIALS = os.getenv("MARATHON_CREDENTIALS", "guest:guest")
MARATHON_AUTH_HEADER = "Basic {}".format(base64.b64encode(MARATHON_CREDENTIALS.encode("utf-8")).decode('utf-8'))

DEFAULT_MARATHON_ADDRESS = "http://127.0.0.1:8080"
DEFAULT_MESOS_ADDRESS = "http://127.0.0.1:5050"

def _build_cors_whitelist(env_value):
    if not env_value:
        return []
    return [_host.strip() for _host in env_value.split(",") if _host.strip()]

def _build_addresses(namespace, option_name, default_address):
    addresses = {addr.rstrip("/") for addr in get_option(namespace, option_name)}
    final_addresses = sorted(list(addresses))
    if not final_addresses:
        final_addresses = [default_address]
    return final_addresses


def _build_marathon_addresses():
    return _build_addresses(namespace="MARATHON", option_name="ADDRESS", default_address=DEFAULT_MARATHON_ADDRESS)

def _build_mesos_addresses():
    return _build_addresses(namespace="MESOS", option_name="ADDRESS", default_address="http://127.0.0.1:5050")

MARATHON_ADDRESSES = _build_marathon_addresses()
MARATHON_LEADER = MARATHON_ADDRESSES[0]

MESOS_ADDRESSES = _build_mesos_addresses()

user, passw = MARATHON_CREDENTIALS.split(':')
marathon_client = MarathonClient(MARATHON_ADDRESSES, username=user, password=passw)

CORS_WHITELIST = _build_cors_whitelist(os.getenv("HOLLOWMAN_CORS_WHITELIST"))

REDIRECT_ROOTPATH_TO = os.getenv("HOLLOWMAN_REDIRECT_ROOTPATH_TO", "/v2/apps")
GOOGLE_OAUTH2_CLIENT_ID = os.getenv("HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_ID", "client_id")
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv("HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_SECRET", "client_secret")

SECRET_KEY = os.getenv("HOLLOWMAN_SECRET_KEY", "secret")
REDIRECT_AFTER_LOGIN = os.getenv("HOLLOWMAN_REDIRECT_AFTER_LOGIN")

HOLLOWMAN_DB_URL = os.getenv("HOLLOWMAN_DB_URL", "sqlite://")
HOLLOWMAN_DB_ECHO = os.getenv("HOLLOWMAN_DB_ECHO", DISABLED) == ENABLED

NEW_RELIC_LICENSE_KEY = os.getenv("NEW_RELIC_LICENSE_KEY")
NEW_RELIC_APP_NAME = os.getenv("NEW_RELIC_APP_NAME")

LOGLEVEL = os.getenv("ASGARD_LOGLEVEL", "INFO")

ASGARD_CACHE_KEY_PREFIX = os.getenv("ASGARD_CACHE_KEY_PREFIX", "asgard/")
ASGARD_CACHE_DEFAULT_TIMEOUT = os.getenv("ASGARD_CACHE_DEFAULT_TIMEOUT", 60)
ASGARD_CACHE_URL = os.getenv("ASGARD_CACHE_URL", "redis://127.0.0.1:6379/0")

