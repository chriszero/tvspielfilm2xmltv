#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Created on 26.04.2013

@author: Chris
'''
import sys
import logging
import logging.handlers
from . import defaults


ERROR = logging.ERROR
WARNING = logging.WARNING
MESSAGE = logging.INFO
DEBUG = logging.DEBUG

# Configure logger
logger = logging.getLogger('tvsp2xmltv')
logger.setLevel(logging.DEBUG)
try:
    sh = logging.handlers.SysLogHandler(address='/dev/log')
    sh.setFormatter(logging.Formatter('%(name)s: %(levelname)s %(message)s'))
    logger.addHandler(sh)
except:
    pass

console = logging.StreamHandler(sys.stdout)
console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s::%(message)s', '%H:%M:%S'))
logger.addHandler(console)


def log(message, level=MESSAGE):
    #print(message)
    if level == MESSAGE:
        logger.info(message)
    if level == DEBUG and defaults.debug:
        logger.debug(message)
    if level == WARNING:
        logger.warning(message)
    if level == ERROR:
        logger.error(message)
