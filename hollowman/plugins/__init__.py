#encoding: utf-8

from enum import Enum
import traceback
import sys

import pkg_resources
from simple_json_logger import JsonLogger

from hollowman.log import logger

class API_PLUGIN_TYPES(Enum):
    API_METRIC_PLUGIN = "asgard_api_metrics_mountpoint"

# Registry é um dict onde a key é o ID do plugin e o value
# são meta-dados sobre o plugin, ex:
#    * ID do plugin
#    * Quais permissões são necessárias para que esse plugin possa ser carregado

# Cada plugins é composto por apenas um arquivo js (main.js), gerado pelo webpack e colocado
# aqui nesse repositório, em `/static/plugins/<plugin-id>/main.js`.

# Todo plugin dever ter o trecho:
#         "info" : {
#            "modules" : [
#               "ui"
#            ],
#         },
# É isso que diz à UI para voltar e pegar o main.js

PLUGIN_REGISTRY = {
}

def register_plugin(plugin_id):
    plugin_data = {
        "id": plugin_id,
        "info": {
            "modules": ["ui"]
        }
    }
    PLUGIN_REGISTRY[plugin_id] = plugin_data

def get_plugin_registry_data():
    return {'plugins': list(PLUGIN_REGISTRY.values())}

def load_entrypoint_group(groupname):
    return list(pkg_resources.iter_entry_points(group=groupname))

def get_plugin_logger_instance(plugin_id):
    return JsonLogger(flatten=True, extra={"plugin-id": plugin_id})


def load_all_metrics_plugins(flask_application, get_plugin_logger_instance=get_plugin_logger_instance):
    all_metric_plugins = load_entrypoint_group(API_PLUGIN_TYPES.API_METRIC_PLUGIN.value)
    for entrypoint in all_metric_plugins:
        try:
            package_name = entrypoint.dist.project_name
            entrypoint_function = entrypoint.load()
            plugin_data = entrypoint_function(logger=get_plugin_logger_instance(plugin_id=package_name))
            url_prefix = f"/_cat/metrics/{package_name}"
            flask_application.register_blueprint(plugin_data['blueprint'], url_prefix=url_prefix)
            logger.info({
                "msg": "Metrics plugin loaded",
                "plugin_entrypoint": entrypoint,
                "plugin_id": package_name,
                "mountpoint URI": url_prefix,
            })
        except Exception as e:
            logger.error({
                "msg": "Failed to load plugin",
                "plugin_entrypoint": entrypoint,
                "plugin_id": package_name,
                "traceback": traceback.format_exc(),
                "type": sys.exc_info()[0].__name__,
            })

