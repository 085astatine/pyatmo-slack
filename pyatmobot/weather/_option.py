# -*- coding: utf-8 -*-

import pathlib
from typing import NamedTuple, Optional
import pyatmo.weather
import slackbot


class DatabaseOption(NamedTuple):
    path: pathlib.Path
    register_favorite_devices: bool
    update_interval: Optional[float]
    update_step: Optional[int]
    sql_log_level: pyatmo.weather.SQLLogging

    @staticmethod
    def option_list(
            name: str,
            help: str = '') -> slackbot.OptionList['DatabaseOption']:
        return slackbot.OptionList(
            DatabaseOption,
            name,
            [slackbot.Option(
                'path',
                type=pathlib.Path,
                required=True,
                help='path to sqlite3 file to record'),
             slackbot.Option(
                'register_favorite_devices',
                default=False,
                type=bool,
                help='whether to register favorite devices in the database'),
             slackbot.Option(
                'update_interval',
                default=600,
                help='database update interval seconds'),
             slackbot.Option(
                'update_step',
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
            help=help)
