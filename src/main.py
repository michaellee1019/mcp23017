import asyncio
import sys
from datetime import timedelta
from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence)

from typing_extensions import Self
from viam.components.board import *
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.proto.component.board import (PowerMode, ReadAnalogReaderResponse,
                                        StreamTicksResponse)
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.streams import Stream


class Board(Board, EasyResource):
    MODEL: ClassVar[Model] = Model(ModelFamily("michaellee1019", "mcp23017"), "board")

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

        async def set(
            self,
            high: bool,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ):
            raise NotImplementedError()

        async def get(
            self,
            *,
            extra: Optional[Dict[str, Any]] = None,
            timeout: Optional[float] = None,
            **kwargs
        ) -> bool:
            raise NotImplementedError()

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
        raise NotImplementedError()

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

