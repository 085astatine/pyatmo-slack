# -*- coding: utf-8 -*-

import datetime
from typing import List, Optional, Sequence, Union
import matplotlib
import numpy
import pyatmo.weather
import pytz
from ._plot_setting import DataSource, MeasurementsField, TimeRange, XAxisMode


def get_data(
        database: pyatmo.weather.Database,
        source: DataSource,
        fields: Union[MeasurementsField, Sequence[MeasurementsField]],
        time_range: TimeRange) -> List[numpy.ndarray]:
    if isinstance(fields, MeasurementsField):
        fields = [fields]
    device_list = [device for device in database.all_device()
                   if source.device.is_target(device)]
    module_list = [
            module
            for device in device_list
            for module in device.modules
            if source.module.is_target(module)]
    result: List[numpy.ndarray] = []
    for module in module_list:
        timezone = pytz.timezone(module.device.timezone)
        measurements_list = database.measurements(
                module,
                int(time_range.origin.timestamp()),
                int(time_range.destination.timestamp()))
        result.append(numpy.array([
                [timezone.localize(
                        datetime.datetime.fromtimestamp(x.timestamp)),
                 *(getattr(x, field.name.lower()) for field in fields)]
                for x in measurements_list]))
    return result


def setup_xaxis(
        axes: matplotlib.axes.Axes,
        time_range: TimeRange,
        mode: XAxisMode,
        with_minor_ticks: bool = False,
        minor_ticks: Optional[Union[int, Sequence[int]]] = None) -> None:
    tzinfo = time_range.tzinfo
    # range
    axes.set_xlim([time_range.origin, time_range.destination])
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
