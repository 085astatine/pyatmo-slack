#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import slackbot
import slackbot.action
import pyatmobot


if __name__ == '__main__':
    # logger
    logger = logging.getLogger('himadobot')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.formatter = logging.Formatter(
                fmt='%(name)s::%(levelname)s::%(message)s')
    logger.addHandler(handler)
    logger.propagate = False
    # bot
    bot = slackbot.create(
                'Sample',
                action_dict={'APILogger': slackbot.action.APILogger,
                             'Pyatmo': pyatmobot.Pyatmo},
                logger=logger)
    bot.start()
