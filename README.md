# mcp23017
The MCP23017 is a GPIO expansion chip that uses i2c to add an additional 16 GPIOs. This module is supported on Raspberry Pi 4B/5 and can supported up to 8 devices on a single i2c network, allowing for up to 128 (16*8) GPIO pins using the default i2c bus of the Raspberry Pi


## Model: michaellee1019:mcp23017:board
This model makes a Viam Board to control the mcp23017. Pins are numbered "0" to "15" for the pins. "0" maps to "A0" and range up to "15" for "B7"

No configuration needed. By default the component will communicate with i2c_address `0x27` on i2c_bus `1`. You can change the i2c_address and i2c_bus in the configuration as shown below. Additionally, all pins are configured with no input pull resistors. To enable the internal pullup resistor on a pin, add the pin number to the `pullups` list in configuration.

This model is implemented using the [Adafruit mcp230xx library](https://docs.circuitpython.org/projects/mcp230xx/en/latest/index.html).

### Configuration
```json
{
  "i2c_bus": 1,
  "i2c_address": "0x27",
  "pullups": [
    "14",
    "15"
  ]
}
```

### Future Work
- Supporting digital interrupts

## Model: michaellee1019:mcp23017:sevensegment
This model supports diplaying characters on two independent seven segment LED display. One character is connected to the "A" pins 0-7 and the other to the B pins. Its not the most efficient use of GPIO pins compared to other devices out there (for example take a look at the modules for [TM1637](https://github.com/michaellee1019/tm1637) and [HT16K33](https://github.com/michaellee1019/ht16k33) modules). But it is useful if you want to control just 1-2 digits and especially useful in testing your datasheet knowledge for how to wire an LED segment display. Each LED is controllable on a `channel` with this model, which is either the A pins or B pins.

### Configuration
```json
{
  "i2c_bus": 1,
  "i2c_address": "0x27",
  "a_direction": "abcdefg",
  "b_direction": "gfedcba"
}
```

| Attribute     | Required? | Default   | Description |
| --------      | -------   | ------    | ------ |
| `i2c_bus`     | No        | `1`       | The i2c bus number to communicate with the `mcp20317`. For example the Raspberry Pi uses bus 1 in most circumstances. |
| `ic2_address` | No        | `"0x27"`  | The i2c address of the `mcp20317` peripheral. The default address of the `mcp20317` is usually `0x27` and can be changed using the `A0-A2` pins. |
| `a_direction` | No        | `gfedcba` | Wiring order of the LED segments on the A channel |
| `b_direction` | No        | `gfedcba` | Wiring order of the LED segments on the B channel |

#### Wiring Order
There are two standards for wiring LED segments: `gfedcba` and `abcdefg`: The most common is `gfedcba`. If you can choose your wiring, this is recommended. This standard seems like a clever ploy for those that can actually say the alphabet backwards, disadvantaging the rest of us. Depending on your wiring between the segment and the mcp23017, choose the corresponding mode based on the mapping below:

gfedcba:
```
mcp23017 pin -> segment letter pin
A/B1 -> g
A/B2 -> f
A/B3 -> e
A/B4 -> d
A/B5 -> c
A/B6 -> b
A/B7 -> a
```

abcdefg:
```
mcp23017 pin -> segment letter pin
A/B1 -> a
A/B2 -> b
A/B3 -> c
A/B4 -> d
A/B5 -> e
A/B6 -> f
A/B7 -> g
```

### Example DoCommands

#### Display Character
Show a single character on the specified channel (A or B).
```json
{
  "display_char": {"char": "8","channel":"A"}
}
```

#### Clear Display
Clear text on the diplay. Equal to having the display render a `" "` space character
```json
{
  "clear": {"channel":"A"}
}
```

#### Flash Word
Cycle through a sequence of characters to display a readable word. Each character will be displayed in order on the channel specified. There will be a delay of the specified seconds between each character.
```json
{
  "flash_word": {"word": "ASDF","channel":"A", "delay_seconds": 0.25}
}
```

## Model: michaellee1019:mcp23017:sensor
This model is a sensor that reads the state of the 16 pins on the mcp23017. It will return a dictionary with the pin number as the key and the value as the state of the pin.

### Configuration
Similar to the `board` model, the `sensor` model requires the `i2c_bus` and `i2c_address` to be specified. Additionally, the `pullups` attribute is used to specify which pins should have internal pullups enabled.
```json
{
  "i2c_bus": 1,
  "i2c_address": "0x27",
  "pullups": [
    14,
    15
  ]
}
```

# michaellee1019:mcp23017:camera
Just kidding!
