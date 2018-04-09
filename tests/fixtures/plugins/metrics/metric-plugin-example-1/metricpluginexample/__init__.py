
import logging
from flask import Blueprint

my_metrics_blue_print = Blueprint(__name__, __name__)

logger = logging.getLogger()

def plugin_init_ok(**kwargs):
    global logger
    if 'logger' in kwargs:
        logger = kwargs['logger']
    return {
    'blueprint': my_metrics_blue_print
    }

def plugin_init_wrong_return(**kwargs):
    return {
        'blueprint': int(42)
    }

def plugin_init_exception(**kwargs):
    return 1/0

@my_metrics_blue_print.route("/ping")
def some_endpoint():
    logger.info("Log from Mertrics Plugin")
    logger.debug("DEBUG Log from Mertrics Plugin")
    return "Metrics Plugin Example 1 OK"

