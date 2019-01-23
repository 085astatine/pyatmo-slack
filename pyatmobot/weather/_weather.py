# -*- coding: utf-8 -*-

import datetime
import logging
import queue
import threading
from typing import Any, Optional
import pyatmo
import pyatmo.weather


class Weather:
    def __init__(
                self,
                config: Any,
                pyatmo_client: pyatmo.Client,
                logger: logging.Logger) -> None:
        self._config = config
        self._logger = logger
        self._database = pyatmo.weather.Database(
                self._config.weather.database_path,
                pyatmo_client,
                logger=self._logger.getChild('database'),
                sql_logging=self._config.weather.sql_log_level)
        # register devices
        self._database.register(
                get_favorites=self._config.weather.register_favorite_devices)
        # update
        self._update_interval: float = config.weather.database_update_interval
        self._update_step: Optional[int] = config.weather.database_update_step
        self._update_thread: Optional[threading.Thread] = None
        self._update_thread_queue: queue.Queue[bool] = queue.Queue(maxsize=1)
        self._update_suspension_limit: Optional[datetime.datetime] = None

    def update(self) -> None:
        # update database
        if (self._update_thread is None
            and (self._update_suspension_limit is None
                 or self._update_suspension_limit < datetime.datetime.now())):
            _start_update_thread(self)
        if (self._update_thread is not None
                and not self._update_thread.is_alive()):
            # database has been updated
            is_updated: bool = self._update_thread_queue.get()
            if is_updated:
                _start_update_thread(self)
            else:
                self._logger.info('database has not been updated')
                self._update_thread = None
                self._update_suspension_limit = (
                        datetime.datetime.now()
                        + datetime.timedelta(seconds=self._update_interval))


def _start_update_thread(self: Weather) -> None:
    self._logger.info('start update thread')
    self._update_thread = threading.Thread(
            target=_update_database,
            args=(self._database,
                  self._update_thread_queue,
                  self._update_step,
                  self._update_interval))
    self._update_thread.start()


def _update_database(
        database: pyatmo.weather.Database,
        result_queue: queue.Queue,
        request_limit: Optional[int],
        min_update_interval: float) -> None:
    is_updated = database.update(
            request_limit=request_limit,
            min_update_interval=min_update_interval)
    result_queue.put(is_updated)
