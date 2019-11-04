# -*- coding: utf-8 -*-

import logging
import pathlib
from typing import Optional
import slack
import yaml
import pyatmo
import slackbot
from ._option import ClientOption, PyatmoOption
from . import weather


class Pyatmo(slackbot.Action[PyatmoOption]):
    def __init__(self,
                 name: str,
                 option: PyatmoOption,
                 logger: Optional[logging.Logger] = None) -> None:
        super().__init__(
                name,
                option,
                logger=logger or logging.getLogger(__name__))
        self._pyatmo_client = _setup_pyatmo_client(
                self.option.pyatmo_client,
                self._logger)
        self._weather = weather.Weather(
                self.option.weather_database,
                self._pyatmo_client,
                logger=self._logger.getChild('weather'))

    def update(
            self,
            client: slack.WebClient) -> None:
        self._weather.update(client)

    @staticmethod
    def option_list(name: str) -> slackbot.OptionList[PyatmoOption]:
        return PyatmoOption.option_list(name)


def _setup_pyatmo_client(
        option: ClientOption,
        logger: logging.Logger) -> pyatmo.Client:
    # load secret
    if not option.secret_file.exists():
        logger.error("secret file '{0}' does not exist"
                     .format(option.secret_file))
    logger.info('open secret file: {0}'.format(option.secret_file))
    with option.secret_file.open() as file:
        secret = yaml.load(file)
        client_id = secret['client_id']
        client_secret = secret['client_secret']
    # create client
    client = pyatmo.Client(
            client_id=client_id,
            client_secret=client_secret,
            scope_list=option.token_scope,
            token_file=option.oauth_token_file,
            request_interval=option.request_interval,
            logger=logger.getChild('client'))
    # initial authenication
    if not option.oauth_token_file.exists():
        logger.info('initial authentication')
        for key in ['username', 'password']:
            if key not in secret:
                logger.error("'{0}' is required in the secret file '{1}'"
                             .format(key, option.secret_file))
        client.authorize(secret['username'], secret['password'])
    return client
