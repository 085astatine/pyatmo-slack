# -*- coding: utf-8 -*-

import datetime
from typing import Optional, Sequence, Union
import matplotlib
from ._plot_setting import XAxisMode




def setup_xaxis(
        axes: matplotlib.axes.Axes,
        origin: datetime.datetime,
        period: datetime.timedelta,
        mode: XAxisMode,
        with_minor_ticks: bool = False,
        minor_ticks: Optional[Union[int, Sequence[int]]] = None) -> None:
    tzinfo = origin.tzinfo
    # range
    axes.set_xlim([origin, origin + period])
    # ticks
    if mode is XAxisMode.YEAR:
        axes.xaxis.set_major_locator(
                matplotlib.dates.YearLocator(tz=tzinfo))
        axes.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter('%Y', tz=tzinfo))
        if with_minor_ticks:
            axes.xaxis.set_minor_locator(
                    matplotlib.dates.MonthLocator(minor_ticks, tz=tzinfo))
            axes.xaxis.set_minor_formatter(
                    matplotlib.dates.DateFormatter('%m', tz=tzinfo))
    elif mode is XAxisMode.MONTH:
        axes.xaxis.set_major_locator(
                matplotlib.dates.MonthLocator(tz=tzinfo))
        axes.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter('%Y-%m', tz=tzinfo))
        if with_minor_ticks:
            axes.xaxis.set_minor_locator(
                    matplotlib.dates.DayLocator(minor_ticks, tz=tzinfo))
            axes.xaxis.set_minor_formatter(
                    matplotlib.dates.DateFormatter('%d', tz=tzinfo))
    elif mode is XAxisMode.DAY:
        axes.xaxis.set_major_locator(
                matplotlib.dates.DayLocator(tz=tzinfo))
        axes.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter('%Y-%m-%d', tz=tzinfo))
        if with_minor_ticks:
            axes.xaxis.set_minor_locator(
                    matplotlib.dates.HourLocator(minor_ticks, tz=tzinfo))
            axes.xaxis.set_minor_formatter(
                    matplotlib.dates.DateFormatter('%H', tz=tzinfo))
    elif mode is XAxisMode.HOUR:
        axes.xaxis.set_major_locator(
                matplotlib.dates.HourLocator(tz=tzinfo))
        axes.xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter('%H', tz=tzinfo))
        if with_minor_ticks:
            axes.xaxis.set_minor_locator(
                    matplotlib.dates.MinuteLocator(minor_ticks, tz=tzinfo))
            axes.xaxis.set_minor_formatter(
                    matplotlib.dates.DateFormatter('%M', tz=tzinfo))
