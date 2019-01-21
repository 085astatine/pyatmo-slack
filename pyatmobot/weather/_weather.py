# -*- coding: utf-8 -*-

import logging
from typing import Any
import pyatmo
import pyatmo.weather


class Weather:
    def __init__(
                self,
                config: Any,
                pyatmo_client: pyatmo.Client,
                logger: logging.Logger) -> None:
        self._config = config
        self._database = pyatmo.weather.Database(
                self._config.weather.database_path,
                pyatmo_client,
                logger=logger.getChild('database'),
                sql_logging=self._config.weather.sql_log_level)
        # register devices
        self._database.register(
                get_favorites=self._config.weather.register_favorite_devices)
