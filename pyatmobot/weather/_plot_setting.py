# -*- coding: utf-8 -*-

import enum


class XAxisMode(enum.Enum):
    YEAR = enum.auto()
    MONTH = enum.auto()
    DAY = enum.auto()
    HOUR = enum.auto()
    AUTO = enum.auto()
