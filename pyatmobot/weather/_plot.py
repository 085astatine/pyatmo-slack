# -*- coding: utf-8 -*-

import datetime
from typing import List, Optional, Sequence, Union
import matplotlib
import numpy
import pyatmo.weather
import pytz
from ._plot_setting import (
        DataSource, FigureFormat, MeasurementsField, PlotSetting, TimeRange,
        XAxisMode, XAxisSetting)


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


def plot(
        database: pyatmo.weather.Database,
        figure_format: FigureFormat,
        title: str,
        default_source: DataSource,
        plot_settings: Sequence[PlotSetting]) -> None:
    figure = matplotlib.figure.Figure(
            figsize=figure_format.figsize(),
            dpi=figure_format.dpi)
    figure.suptitle(title)
    axes_list = [
            figure.add_subplot(
                    figure_format.rows,
                    figure_format.columns,
                    i)
            for i in range(1, figure_format.rows * figure_format.columns + 1)]
    for plot_setting in plot_settings:
        axes = axes_list[plot_setting.position - 1]
        for value in plot_setting.values:
            data_list = get_data(
                    database,
                    default_source.override(value.source),
                    value.field,
                    plot_setting.time_range.shifted(value.time_shift))
            for data in data_list:
                axes.plot(
                        data[:, 0] - value.time_shift,
                        data[:, 1],
                        label=value.label)
        if any(value.label for value in plot_setting.values):
            axes.legend(loc='best')
        axes.grid(True)
        setup_xaxis(
                axes,
                plot_setting.time_range,
                plot_setting.x_axis.mode,
                plot_setting.x_axis.with_minor_ticks,
                plot_setting.x_axis.minor_ticks)
    figure.autofmt_xdate()
    figure.savefig(
            '{0}.{1}'.format(title, figure_format.format.name.lower()),
            format=figure_format.format.name.lower())
