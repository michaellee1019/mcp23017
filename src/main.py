import asyncio
import subprocess
from datetime import timedelta
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence

from typing_extensions import Self
from viam.components.board import Board, TickStream
from viam.components.generic import Generic
from viam.components.sensor import Sensor
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.proto.component.board import PowerMode
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes
from viam import logging

import digitalio

import smbus
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_mcp230xx.digital_inout import DigitalInOut
from adafruit_extended_bus import ExtendedI2C as I2C

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

LOGGER = logging.getLogger(__name__)

class MCP23017Board(Board, EasyResource):
    MODEL: ClassVar[Model] = Model(ModelFamily("michaellee1019", "mcp23017"), "board")
    i2c: I2C
    i2c_bus: int = 1
    i2c_address: int = 0x27
    mcp: MCP23017
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
        if "i2c_bus" in config.attributes.fields:
            self.i2c_bus = int(config.attributes.fields["i2c_bus"].string_value)
        self.i2c = I2C(self.i2c_bus)
        if "i2c_address" in config.attributes.fields:
            self.i2c_address = int(
                config.attributes.fields["i2c_address"].string_value, base=16
            )
        if "pullups" in config.attributes.fields:
            self.pullups = [
                int(x) for x in config.attributes.fields["pullups"].list_value
            ]

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
            **kwargs,
        ) -> Board.Analog.Value:
            raise NotImplementedError()

        async def write(
            self,
            value: int,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs,
        ):
            raise NotImplementedError()

    class DigitalInterrupt(Board.DigitalInterrupt):

        async def value(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs,
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
            **kwargs,
        ):
            if self.pin.direction:
                self.pin.switch_to_output()
            self.pin.value = high

        async def get(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs,
        ) -> bool:
            if not self.pin.direction:
                self.pin.switch_to_input()
            return self.pin.value

        async def get_pwm(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs,
        ) -> float:
            raise NotImplementedError()

        async def set_pwm(
            self,
            duty_cycle: float,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs,
        ):
            raise NotImplementedError()

        async def get_pwm_frequency(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs,
        ) -> int:
            raise NotImplementedError()

        async def set_pwm_frequency(
            self,
            frequency: int,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs,
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
        **kwargs,
    ):
        raise NotImplementedError()

    async def stream_ticks(
        self,
        interrupts: List[DigitalInterrupt],
        *,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> TickStream:
        raise NotImplementedError()

class MCP23017Sensor(Sensor, EasyResource):
    MODEL = "michaellee1019:mcp23017:sensor"
    i2c: I2C
    i2c_bus: int = 1
    i2c_address: int = 0x27
    mcp: MCP23017
    pins: List[DigitalInOut]
    pullups: List[int] = []

    @classmethod
    def new(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        output = self(config.name)
        output.reconfigure(config, dependencies)
        return output

    def reconfigure(self,
                    config: ComponentConfig,
                    dependencies: Mapping[ResourceName, ResourceBase]):
        if "i2c_bus" in config.attributes.fields:
            self.i2c_bus = int(config.attributes.fields["i2c_bus"].string_value)
        self.i2c = I2C(self.i2c_bus)
        if "i2c_address" in config.attributes.fields:
            self.i2c_address = int(
                config.attributes.fields["i2c_address"].string_value, base=16
            )
        if "pullups" in config.attributes.fields:
            self.pullups = [
                int(x) for x in config.attributes.fields["pullups"].list_value
            ]

        self.mcp = MCP23017(self.i2c, self.i2c_address)
        self.pins = [self.mcp.get_pin(i) for i in range(16)]

        for i in range(16):
            if i in self.pullups:
                self.pins[i].pull = digitalio.Pull.UP
            else:
                self.pins[i].pull = None

        return super().reconfigure(config, dependencies)

    async def get_readings(self, **kwargs):
        readings = {}
        for idx, pin in enumerate(self.pins):
            if not pin.direction:
                pin.switch_to_input()
            readings[str(idx)] = pin.value
        return readings

segment_char_mappings = {
    "A": {"gfedcba": 0x77, "abcdefg": 0x77},
    "a": {"gfedcba": 0x7D, "abcdefg": 0x5F},
    "b": {"gfedcba": 0x1F, "abcdefg": 0x7C},
    "C": {"gfedcba": 0x4E, "abcdefg": 0x39},
    "c": {"gfedcba": 0x0D, "abcdefg": 0x58},
    "d": {"gfedcba": 0x3D, "abcdefg": 0x5E},
    "E": {"gfedcba": 0x4F, "abcdefg": 0x79},
    "F": {"gfedcba": 0x47, "abcdefg": 0x71},
    "G": {"gfedcba": 0x5E, "abcdefg": 0x3D},
    "H": {"gfedcba": 0x37, "abcdefg": 0x76},
    "h": {"gfedcba": 0x17, "abcdefg": 0x74},
    "I": {"gfedcba": 0x06, "abcdefg": 0x30},
    "J": {"gfedcba": 0x3C, "abcdefg": 0x1E},
    "L": {"gfedcba": 0x0E, "abcdefg": 0x38},
    "n": {"gfedcba": 0x15, "abcdefg": 0x54},
    "O": {"gfedcba": 0x7E, "abcdefg": 0x3F},
    "o": {"gfedcba": 0x1D, "abcdefg": 0x5C},
    "P": {"gfedcba": 0x67, "abcdefg": 0x73},
    "q": {"gfedcba": 0x73, "abcdefg": 0x67},
    "r": {"gfedcba": 0x05, "abcdefg": 0x50},
    "S": {"gfedcba": 0x5B, "abcdefg": 0x6D},
    "t": {"gfedcba": 0x0F, "abcdefg": 0x78},
    "U": {"gfedcba": 0x3E, "abcdefg": 0x3E},
    "u": {"gfedcba": 0x1C, "abcdefg": 0x1C},
    "y": {"gfedcba": 0x3B, "abcdefg": 0x6E},
    "0": {"gfedcba": 0x7E, "abcdefg": 0x3F},
    "1": {"gfedcba": 0x30, "abcdefg": 0x06},
    "2": {"gfedcba": 0x6D, "abcdefg": 0x5B},
    "3": {"gfedcba": 0x79, "abcdefg": 0x4F},
    "4": {"gfedcba": 0x33, "abcdefg": 0x66},
    "5": {"gfedcba": 0x5B, "abcdefg": 0x6D},
    "6": {"gfedcba": 0x5F, "abcdefg": 0x7D},
    "7": {"gfedcba": 0x70, "abcdefg": 0x07},
    "8": {"gfedcba": 0x7F, "abcdefg": 0x7F},
    "9": {"gfedcba": 0x7B, "abcdefg": 0x6F},
    " ": {"gfedcba": 0x00, "abcdefg": 0x00}
}

class MCP23017SevenSegmentLED(Generic, EasyResource):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("michaellee1019", "mcp23017"), "seven_segment_led"
    )
    i2c_bus: int = 1
    i2c_address: int = 0x27
    i2c = None

    a_direction: str = "gfedcba"
    b_direction: str = "gfedcba"

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        return super().new(config, dependencies)

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        # LOGGER.error(f"reconfiguring with: {config}")
        if "i2c_bus" in config.attributes.fields:
            self.i2c_bus = int(config.attributes.fields["i2c_bus"].number_value)
        if "i2c_address" in config.attributes.fields:
            self.i2c_address = int(config.attributes.fields["i2c_address"].string_value, base=16)
        if "a_direction" in config.attributes.fields:
            self.a_direction = config.attributes.fields["a_direction"].string_value
        if "b_direction" in config.attributes.fields:
            self.b_direction = config.attributes.fields["b_direction"].string_value

        try:
            self.i2c = smbus.SMBus(self.i2c_bus)
        except Exception as e:
            raise ValueError(f"i2c bus connection error on bus number '{self.i2c_bus}'. Check if your 'i2c_bus' attribute is correct", e)

        # Configue the register to default value
        for addr in range(22):
            if (addr == 0) or (addr == 1):
                self.i2c.write_byte_data(self.i2c_address, addr, 0xFF)
            else:
                self.i2c.write_byte_data(self.i2c_address, addr, 0x00)

        # configue all PinA + PinB output
        self.i2c.write_byte_data(self.i2c_address, MCP23017_IODIRA, 0x00)
        self.i2c.write_byte_data(self.i2c_address, MCP23017_IODIRB, 0x00)

        return super().reconfigure(config, dependencies)

    @classmethod
    def validate_config(self, config: ComponentConfig) -> None:
        # Custom validation can be done by specifiying a validate function like this one. Validate functions
        # can raise errors that will be returned to the parent through gRPC. Validate functions can
        # also return a sequence of strings representing the implicit dependencies of the resource.
        return None

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Mapping[str, ValueTypes]:
        result = {key: False for key in command.keys()}
        for name, args in command.items():
            if name == "flash_word":
                if "word" in args and "channel" in args and "delay_seconds" in args:
                    results = await self.flash_word(args["word"], args["channel"], args["delay_seconds"])
                    result[name] = "flashed: " + results
                else:
                    result[name] = "missing 'word', 'channel', and/or 'delay_seconds' key."
            if name == "display_char":
                if "char" in args and "channel" in args:
                    results = await self.display_char(args["char"], args["channel"])
                else: result[name] = "missing 'char', and/or 'channel' key."
            if name == "clear":
                if "channel" in args:
                    results = await self.clear(args["channel"])
                else: result[name] = "missing 'channel' key."
        return result

    def get_register(self, channel: str):
        if channel is not 'A' and channel is not 'B':
            raise ValueError("channel must be either 'A' or 'B'")
        return MCP23017_GPIOA if channel == 'A' else MCP23017_GPIOB

    def best_match_mapping(self, char: chr):
        return segment_char_mappings.get(
                char,
                segment_char_mappings.get(
                    char.lower(), segment_char_mappings.get(char.upper())
                ),
            )

    async def flash_word(self, word: str, channel: str, delay: float) -> str:
        for char in word:
            mapping = self.best_match_mapping(char)
            a_or_b_register = self.get_register(channel)
            if mapping is not None:

                self.i2c.write_byte_data(
                    self.i2c_address, a_or_b_register, mapping[self.a_direction]
                )

                await asyncio.sleep(delay)

                self.i2c.write_byte_data(self.i2c_address, a_or_b_register, 0x00)

                await asyncio.sleep(delay)

        return word

    async def display_char(self, char: chr, channel: str) -> None:
        mapping = self.best_match_mapping(char)
        a_or_b_register = self.get_register(channel)

        self.i2c.write_byte_data(
            self.i2c_address, a_or_b_register, mapping[self.a_direction]
        )
        
        return True

    async def clear(self, channel: str) -> None:
        a_or_b_register = self.get_register(channel)

        self.i2c.write_byte_data(
            self.i2c_address, a_or_b_register, 0x00
        )

        return True


def check_and_enable_i2c():
    try:
        # Check the current I2C configuration
        result = subprocess.run(
            ["sudo", "raspi-config", "nonint", "get_i2c"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Get the returned output and strip any whitespace
        i2c_status = result.stdout.strip()

        # If the status is 1, enable I2C
        if i2c_status == "1":
            LOGGER.info("I2C is disabled. Enabling it now...")
            subprocess.run(
                ["sudo", "raspi-config", "nonint", "do_i2c", "0"], check=True
            )
            LOGGER.info("I2C has been enabled.")
        else:
            LOGGER.info("I2C is already enabled.")

    except subprocess.CalledProcessError as e:
        LOGGER.error(f"Error executing command: {e}")
        LOGGER.error(f"Output: {e.output}")
    except Exception as e:
        LOGGER.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    check_and_enable_i2c()
    asyncio.run(Module.run_from_registry())
