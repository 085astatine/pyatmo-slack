# -*- coding: utf-8 -*-

import pathlib
from typing import List, NamedTuple, Optional, Union
import pyatmo
import slackbot
from . import weather


class ClientOption(NamedTuple):
    secret_file: pathlib.Path
    oauth_token_file: pathlib.Path
    token_scope: Optional[List[pyatmo.Scope]]
    request_interval: Optional[float]

    @staticmethod
    def option_list(
            name: str,
            help: str = '') -> slackbot.OptionList['ClientOption']:
        return slackbot.OptionList(
            ClientOption,
            name,
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
                action=_parse_scope,
                sample=['read_station'],
                help='scope required by token'),
             slackbot.Option(
                'request_interval',
                default=1.0,
                action=lambda x: float(x) if x is not None else None,
                help='minimum interval seconds between API requests')],
            help=help)


def _parse_scope(
        value: Union[None, str, List[str]]) -> Optional[List[pyatmo.Scope]]:
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


class PyatmoOption(NamedTuple):
    pyatmo_client: ClientOption
    weather_database: weather.DatabaseOption

    @staticmethod
    def option_list(
            name: str,
            help: str = '') -> slackbot.OptionList['PyatmoOption']:
        return slackbot.OptionList(
                PyatmoOption,
                name,
                [ClientOption.option_list(
                        'pyatmo_client',
                        help='pyatmo API client'),
                 weather.DatabaseOption.option_list(
                        'weather_database',
                        help='weather database')],
                help=help)
