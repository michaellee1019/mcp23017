import asyncio

from datetime import timedelta
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence

from typing_extensions import Self
from viam.components.board import Board, TickStream
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.proto.component.board import PowerMode
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily

import digitalio
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_mcp230xx.digital_inout import DigitalInOut

MCP23017_IODIRA = 0x00
MCP23017_IPOLA = 0x02
MCP23017_GPINTENA = 0x04
MCP23017_DEFVALA = 0x06
MCP23017_INTCONA = 0x08
MCP23017_IOCONA = 0x0A
MCP23017_GPPUA = 0x0C
MCP23017_INTFA = 0x0E
MCP23017_INTCAPA = 0x10
MCP23017_GPIOA = 0x12
MCP23017_OLATA = 0x14

MCP23017_IODIRB = 0x01
MCP23017_IPOLB = 0x03
MCP23017_GPINTENB = 0x05
MCP23017_DEFVALB = 0x07
MCP23017_INTCONB = 0x09
MCP23017_IOCONB = 0x0B
MCP23017_GPPUB = 0x0D
MCP23017_INTFB = 0x0F
MCP23017_INTCAPB = 0x11
MCP23017_GPIOB = 0x13
MCP23017_OLATB = 0x15


class MCP23017Board(Board, EasyResource):
    MODEL: ClassVar[Model] = Model(ModelFamily("michaellee1019", "mcp23017"), "board")
    i2c: busio.I2C = None
    i2c_address: int = 0x27
    mcp: MCP23017 = None
    pins: List[DigitalInOut]
    pullups: List[int] = []

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Board component.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        return []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        # if "i2c_bus" in config.attributes.fields:
        #     self.i2c_bus = int(config.attributes.fields["i2c_bus"].string_value)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        if "i2c_address" in config.attributes.fields:
            self.i2c_address = int(
                config.attributes.fields["i2c_address"].string_value, base=16
            )
        if "pullups" in config.attributes.fields:
            self.pullups = [int(x) for x in config.attributes.fields["pullups"].list_value]

        self.mcp = MCP23017(self.i2c, self.i2c_address)
        self.pins = [self.mcp.get_pin(i) for i in range(16)]
        for i in range(16):
            if i in self.pullups:
                self.pins[i].pull = digitalio.Pull.UP
            else:
                self.pins[i].pull = None

        return super().reconfigure(config, dependencies)

    class Analog(Board.Analog):

        async def read(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ) -> Board.Analog.Value:
            raise NotImplementedError()

        async def write(
            self,
            value: int,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ):
            raise NotImplementedError()

    class DigitalInterrupt(Board.DigitalInterrupt):

        async def value(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ) -> int:
            raise NotImplementedError()

    class GPIOPin(Board.GPIOPin):
        pin: DigitalInOut = None

        def __init__(self, name: str, pin: DigitalInOut):
            self.pin = pin
            super().__init__(name)

        async def set(
            self,
            high: bool,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ):
            if self.pin.direction:
                self.pin.switch_to_output()
            self.pin.value = high

        async def get(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ) -> bool:
            if not self.pin.direction:
                self.pin.switch_to_input()
            return self.pin.value

        async def get_pwm(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ) -> float:
            raise NotImplementedError()

        async def set_pwm(
            self,
            duty_cycle: float,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ):
            raise NotImplementedError()

        async def get_pwm_frequency(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ) -> int:
            raise NotImplementedError()

        async def set_pwm_frequency(
            self,
            frequency: int,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ):
            raise NotImplementedError()

    async def analog_by_name(self, name: str) -> Analog:
        raise NotImplementedError()

    async def digital_interrupt_by_name(self, name: str) -> DigitalInterrupt:
        raise NotImplementedError()

    async def gpio_pin_by_name(self, name: str) -> GPIOPin:
        try:
            pin_num = int(name)
            pin = self.pins[pin_num]
            return MCP23017Board.GPIOPin(name, pin)
        except ValueError as ex:
            raise ValueError("pin name must be an integer between 0-15") from ex

    async def analog_names(self) -> List[str]:
        raise NotImplementedError()

    async def digital_interrupt_names(self) -> List[str]:
        raise NotImplementedError()

    async def set_power_mode(
        self,
        mode: PowerMode.ValueType,
        duration: Optional[timedelta] = None,
        *,
        timeout: Optional[float] = None,
        **kwargs
    ):
        raise NotImplementedError()

    async def stream_ticks(
        self,
        interrupts: List[DigitalInterrupt],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> TickStream:
        raise NotImplementedError()


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
