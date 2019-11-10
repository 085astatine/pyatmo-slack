# -*- coding: utf-8 -*-

import enum
from typing import NamedTuple, Optional, Union
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


class XAxisMode(enum.Enum):
    YEAR = enum.auto()
    MONTH = enum.auto()
    DAY = enum.auto()
    HOUR = enum.auto()
    AUTO = enum.auto()
