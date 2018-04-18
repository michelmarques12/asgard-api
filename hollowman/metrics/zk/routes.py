
import json
import os
from http import HTTPStatus

from flask import Blueprint, make_response

from .telnet import send_command
from .parser import parse_stat_output

from asgard.sdk.options import get_option

zk_metrics_blueprint = Blueprint(__name__, __name__)


@zk_metrics_blueprint.route("/<int:myid>")
def zk_metrics(myid):
    ZK_IP = os.getenv("HOLLOWMAN_METRICS_ZK_ID_{}".format(myid - 1))
    if not ZK_IP:
        return make_response("{}", HTTPStatus.NOT_FOUND)

    res = parse_stat_output(send_command(ZK_IP, 2181, "stat").decode("utf8"))
    response = make_response(json.dumps(res), HTTPStatus.OK)
    response.headers['Content-type'] = "application/json"
    return response


@zk_metrics_blueprint.route("/leader")
def zk_leader():
    zk_ips = get_option("metrics", "zk_id")
    data = []
    for ip in zk_ips:
        metrics = parse_stat_output(send_command(ip, 2181, "stat").decode("utf8"))
        data.append(metrics)

    all_modes = [metric.get("mode") == "leader" for metric in data]
    if any(all_modes):
        return json.dumps({"leader": all_modes.index(True) + 1})

    return json.dumps({"leader": 0})
