# mcp23017
The MCP23017 is a GPIO expansion chip that uses i2c to add an additional 16 GPIOs. This module is supported on Raspberry Pi 4B/5 and can supported up to 8 devices on a single i2c network, allowing for up to 128 (16*8) GPIO pins using the default i2c bus of the Raspberry Pi


# michaellee1019:mcp23017:board
This model makes a Viam Board to control the mcp23017. Pins are numbered "0" to "15" for the pins. "0" maps to "A0" and range up to "15" for "B7"

No configuration needed. By default the i2c_address is `0x27` and can be configured with a different `i2c_address` as shown below. Additionally, all pins are configured with no input pull resistors. To enable the internal pullup resistor on a pin, add the pin number to the `pullups` list in configuration.

This model is implemented using the [Adafruit mcp230xx library](https://docs.circuitpython.org/projects/mcp230xx/en/latest/index.html).

## Configuration
```
{
  "i2c_address": "0x27",
  "pullups": [
    "14",
    "15"
  ]
}
```

## Future Work
- Supporting digital interrupts

# michaellee1019:mcp23017:eightsegment
TODO