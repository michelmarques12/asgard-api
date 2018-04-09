#encoding: utf-8
import os
import logging

from simple_json_logger import JsonLogger

from hollowman import conf

logger = JsonLogger(flatten=True)
logger.setLevel(getattr(logging, conf.LOGLEVEL, logging.INFO))

dev_null_logger = JsonLogger(flatten=True, stream=open(os.devnull, "w"))
dev_null_logger.setLevel(logging.DEBUG)
