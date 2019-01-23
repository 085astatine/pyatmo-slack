# -*- coding: utf-8 -*-

import logging
import pathlib
from typing import Any, Dict, List, Optional
import yaml
import pyatmo
import slackbot
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
    def option_list(name: str) -> slackbot.OptionList:
        pyatmo_client_option = slackbot.OptionList(
            'pyatmo_client',
            [slackbot.Option(
                'secret_file',
                type=pathlib.Path,
                required=True,
                help='YAML file with'
                     ' client_id & client_secret. '
                     '(required only for initial authentication:'
                     ' username & password)'),
             slackbot.Option(
                'oauth_token_file',
                type=pathlib.Path,
                required=True,
                help='path to the file to save & load oauth tokens'),
             slackbot.Option(
                'token_scope',
                action=_parse_token,
                sample=['read_station'],
                help='scope required by token'),
             slackbot.Option(
                'request_interval',
                default=1.0,
                action=lambda x: float(x) if x is not None else None,
                help='minimum interval seconds between API requests')],
            help='pyatmo API client')
        weather_option = slackbot.OptionList(
            'weather',
            [slackbot.Option(
                'database_path',
                type=pathlib.Path,
                required=True,
                help='path to sqlite3 file to record'),
             slackbot.Option(
                'register_favorite_devices',
                default=False,
                type=bool,
                help='whether to register favorite devices in the database'),
             slackbot.Option(
                'database_update_interval',
                default=600,
                help='database update interval seconds'),
             slackbot.Option(
                'database_update_step',
                action=lambda x: int(x) if x is not None else None,
                default=10,
                help='number of API requests per update (unlimited if None)'),
             slackbot.Option(
                'sql_log_level',
                action=lambda x: getattr(pyatmo.weather.SQLLogging, x.upper()),
                default='none',
                choices=[str(x.name).lower()
                         for x in pyatmo.weather.SQLLogging],
                help='print sql statement & row')],
            help='weather database')
        return slackbot.OptionList(
            name,
            [pyatmo_client_option,
             weather_option])


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


def _parse_token(value: Any) -> Optional[List[pyatmo.Scope]]:
    # None -> None
    if value is None:
        return None
    # str -> [str]
    if isinstance(value, str):
        value = [value]
    result: List[pyatmo.Scope] = []
    for x in value:
        for scope in pyatmo.Scope:
            if str(scope) == x:
                result.append(scope)
                break
        else:
            message = "'{0}' is an invalid value for scope.".format(x)
            raise slackbot.OptionError(message)
    return sorted(result)
