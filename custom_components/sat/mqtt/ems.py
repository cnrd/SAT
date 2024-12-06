from __future__ import annotations

import logging

from homeassistant.core import Event

from . import SatMqttCoordinator
from ..coordinator import DeviceState

DATA_FLAME_ACTIVE = "burngas"
DATA_DHW_SETPOINT = "dhw/seltemp"
DATA_CONTROL_SETPOINT = "selflowtemp"
DATA_REL_MOD_LEVEL = "curburnpow"
DATA_BOILER_TEMPERATURE = "curflowtemp"
DATA_RETURN_TEMPERATURE = "rettemp"

DATA_DHW_ENABLE = "tapwateractive"
DATA_CENTRAL_HEATING = "heatingactive"
DATA_BOILER_CAPACITY = "nompower"

DATA_REL_MIN_MOD_LEVEL = "burnminnpower"
DATA_MAX_REL_MOD_LEVEL_SETTING = "burnmaxpower"

_LOGGER: logging.Logger = logging.getLogger(__name__)


class SatEmsMqttCoordinator(SatMqttCoordinator):
    """Class to manage fetching data from the OTGW Gateway using MQTT."""

    @property
    def supports_setpoint_management(self) -> bool:
        return True

    @property
    def supports_hot_water_setpoint_management(self) -> bool:
        return True

    @property
    def supports_maximum_setpoint_management(self) -> bool:
        return True

    @property
    def supports_relative_modulation_management(self) -> bool:
        return True

    @property
    def device_active(self) -> bool:
        return self.data.get(DATA_CENTRAL_HEATING)

    @property
    def flame_active(self) -> bool:
        return self.data.get(DATA_FLAME_ACTIVE)

    @property
    def hot_water_active(self) -> bool:
        return self.data.get(DATA_DHW_ENABLE)

    @property
    def setpoint(self) -> float | None:
        return self.data.get(DATA_CONTROL_SETPOINT)

    @property
    def hot_water_setpoint(self) -> float | None:
        return self.data.get(DATA_DHW_SETPOINT)

    @property
    def boiler_temperature(self) -> float | None:
        return self.data.get(DATA_BOILER_TEMPERATURE)

    @property
    def return_temperature(self) -> float | None:
        return self.data.get(DATA_RETURN_TEMPERATURE)

    @property
    def relative_modulation_value(self) -> float | None:
        return self.data.get(DATA_REL_MOD_LEVEL)

    @property
    def boiler_capacity(self) -> float | None:
        value = self.data.get(DATA_BOILER_CAPACITY)
        return float(value) if value is not None else super().boiler_capacity

    @property
    def minimum_relative_modulation_value(self) -> float | None:
        value = self.data.get(DATA_REL_MIN_MOD_LEVEL)
        return float(value) if value is not None else super().minimum_relative_modulation_value

    @property
    def maximum_relative_modulation_value(self) -> float | None:
        value = self.data.get(DATA_MAX_REL_MOD_LEVEL_SETTING)
        return float(value) if value is not None else super().maximum_relative_modulation_value

    @property
    def member_id(self) -> int | None:
        # Not supported (yet)
        return None

    async def boot(self) -> SatMqttCoordinator:
        # Nothing needs to be booted (yet)
        return self

    def get_tracked_entities(self) -> list[str]:
        return [
            DATA_CENTRAL_HEATING,
            DATA_FLAME_ACTIVE,
            DATA_DHW_ENABLE,
            DATA_DHW_SETPOINT,
            DATA_CONTROL_SETPOINT,
            DATA_REL_MOD_LEVEL,
            DATA_BOILER_TEMPERATURE,
            DATA_BOILER_CAPACITY,
            DATA_REL_MIN_MOD_LEVEL,
            DATA_MAX_REL_MOD_LEVEL_SETTING,
        ]

    async def async_state_change_event(self, _event: Event) -> None:
        if self._listeners:
            self._schedule_refresh()

        self.async_update_listeners()

    async def async_set_control_setpoint(self, value: float) -> None:
        await self._publish_command(f'{{"cmd": "selflowtemp", "value": {0 if value == 10 else value}}}')
        await super().async_set_control_setpoint(value)

    async def async_set_control_hot_water_setpoint(self, value: float) -> None:
        await self._publish_command(f'{{"cmd": "dhw/seltemp", "value": {value}}}')
        await super().async_set_control_hot_water_setpoint(value)

    async def async_set_control_thermostat_setpoint(self, value: float) -> None:
        # Not supported (yet)
        await super().async_set_control_thermostat_setpoint(value)

    async def async_set_heater_state(self, state: DeviceState) -> None:
        if state == DeviceState.OFF:
            await self.async_set_control_setpoint(0)

        await super().async_set_heater_state(state)

    async def async_set_control_max_relative_modulation(self, value: int) -> None:
        await self._publish_command(f'{{"cmd": "burnmaxpower", "value": {value}}}')

        await super().async_set_control_max_relative_modulation(value)

    async def async_set_control_max_setpoint(self, value: float) -> None:
        await self._publish_command(f'{{"cmd": "heatingtemp", "value": {value}}}')

        await super().async_set_control_max_setpoint(value)

    def _get_topic_for_subscription(self, key: str) -> str:
        return f"{self._topic}/{self.device_id}/{key}"

    def _get_topic_for_publishing(self) -> str:
        return f"{self._topic}/{self.device_id}/boiler"
