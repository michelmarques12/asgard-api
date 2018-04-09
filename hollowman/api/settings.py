from flask import Blueprint, request, Response
import json
import logging

from hollowman import log
from hollowman.plugins import ASGARD_PLUGIN_LOGGER_REGISTRY

settings_blueprint = Blueprint(__name__, __name__)

@settings_blueprint.route("/settings", methods=["POST"])
def settings():
    log.logger.debug("Mudando settings")
    data = request.get_json()
    loglevel = data.get("loglevel", "INFO")
    new_loglevel = getattr(logging, loglevel, logging.INFO)
    log.logger.setLevel(new_loglevel)
    for plugin_id, logger in ASGARD_PLUGIN_LOGGER_REGISTRY.items():
        old_loglevel = logging.getLevelName(logger.getEffectiveLevel())
        log.logger.debug({"action": "change-log-level", "plugin": plugin_id, "old-loglevel": old_loglevel, "new-loglevel": logging.getLevelName(new_loglevel)})
        logger.setLevel(new_loglevel)
    return Response(json.dumps({"loglevel": logging.getLevelName(new_loglevel)}), status=200)
