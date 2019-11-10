# -*- coding: utf-8 -*-

import datetime
import enum
from typing import NamedTuple, Optional, Tuple, Union
import pyatmo.weather


class MeasurementsField(enum.Enum):
    TEMPERATURE = enum.auto()
    HUMIDITY = enum.auto()
    PRESSURE = enum.auto()
    CO2 = enum.auto()
    RAIN = enum.auto()
    WIND_STRENGTH = enum.auto()
    WIND_ANGLE = enum.auto()
    GUST_STRENGTH = enum.auto()
    GUST_ANGLE = enum.auto()


class DeviceSpecifier(NamedTuple):
    id: Optional[str] = None
    name: Optional[str] = None

    def is_effective(self) -> bool:
        return self.id is not None or self.name is not None

    def is_target(
            self,
            target: Union[pyatmo.weather.Device, pyatmo.weather.Module]
            ) -> bool:
        return ((self.id is None or self.id == target.id)
                and (self.name is None or self.name == target.name))


class DataSource(NamedTuple):
    device: DeviceSpecifier = DeviceSpecifier()
    module: DeviceSpecifier = DeviceSpecifier()

    def override(self, other: 'DataSource') -> 'DataSource':
        device = self.device
        module = self.module
        if other.device.is_effective():
            device = other.device
            module = DeviceSpecifier()
        if other.module.is_effective():
            module = other.module
        return DataSource(
                device=device,
                module=module)


class TimeRange(NamedTuple):
    origin: datetime.datetime
    period: datetime.timedelta

    @property
    def destination(self) -> datetime.datetime:
        return self.origin + self.period

    @property
    def tzinfo(self) -> Optional[datetime.tzinfo]:
        return self.origin.tzinfo

    def shifted(self, delta: datetime.timedelta) -> 'TimeRange':
        return TimeRange(
                origin=self.origin + delta,
                period=self.period)


class ImageFileFormat(enum.Enum):
    PNG = enum.auto()
    JPG = enum.auto()
    PDF = enum.auto()
    SVG = enum.auto()


class FigureFormat(NamedTuple):
    width: float = 6.4
    height: float = 4.8
    dpi: float = 100.0
    format: ImageFileFormat = ImageFileFormat.PNG

    def figsize(self) -> Tuple[float, float]:
        return (self.width, self.height)


class XAxisMode(enum.Enum):
    YEAR = enum.auto()
    MONTH = enum.auto()
    DAY = enum.auto()
    HOUR = enum.auto()
    AUTO = enum.auto()
