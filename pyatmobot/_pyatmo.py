# -*- coding: utf-8 -*-

import logging
import pathlib
from typing import Any, Dict, List, Optional
import yaml
import pyatmo
import slackbot
from ._option import PyatmoOption
from . import weather


class Pyatmo(slackbot.Action):
    def __init__(self,
                 name: str,
                 config: Any,
                 logger: Optional[logging.Logger] = None) -> None:
        super().__init__(
                name,
                config,
                logger=logger or logging.getLogger(__name__))
        self._pyatmo_client = _setup_pyatmo_client(
                self.config.pyatmo_client.secret_file,
                self.config.pyatmo_client.oauth_token_file,
                self.config.pyatmo_client.token_scope,
                self.config.pyatmo_client.request_interval,
                self._logger)
        self._weather = weather.Weather(
                self.config,
                self._pyatmo_client,
                logger=self._logger.getChild('weather'))

    def run(self, api_list: List[Dict[str, Any]]) -> None:
        self._weather.update()

    @staticmethod
    def option_list(name: str) -> slackbot.OptionList[PyatmoOption]:
        return PyatmoOption.option_list(name)


def _setup_pyatmo_client(
        secret_file: pathlib.Path,
        oauth_token_file: pathlib.Path,
        scope_list: Optional[List[pyatmo.Scope]],
        request_interval: Optional[float],
        logger: logging.Logger) -> pyatmo.Client:
    # load secret
    if not secret_file.exists():
        logger.error("secret file '{0}' does not exist".format(secret_file))
    logger.info('open secret file: {0}'.format(secret_file))
    with secret_file.open() as file:
        secret = yaml.load(file)
        client_id = secret['client_id']
        client_secret = secret['client_secret']
    # create client
    client = pyatmo.Client(
            client_id=client_id,
            client_secret=client_secret,
            scope_list=scope_list,
            token_file=oauth_token_file,
            request_interval=request_interval,
            logger=logger.getChild('client'))
    # initial authenication
    if not oauth_token_file.exists():
        logger.info('initial authentication')
        for key in ['username', 'password']:
            if key not in secret:
                logger.error("'{0}' is required in the secret file '{1}'"
                             .format(key, secret_file))
        client.authorize(secret['username'], secret['password'])
    return client
