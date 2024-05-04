# Software
## CircuitPython
This code has been written using [Adafruit CircuitPython](https://circuitpython.org).
Honestely though, this is such a simple project it could easily be ported to micropython, but I don't currently have time to do that.
## Microcontroller
This code has been tested on the [Waveshare RP2040-Zero](https://www.waveshare.com/rp2040-zero.htm), so if porting to another board all you *should* have to do is change the pins to valid pins on your board.

## How it Works
I kind of wanted to write a blog style post for this project, so here's how the code works.

```python
import time, board, neopixel, analogio, pulseio, array
from digitalio import DigitalInOut, Direction, Pull
```
This may look complicated, but it can be expanded for better readability to:
```python
import time
import board
import neopixel
import analogio
import pulseio
import array
from digitalio import DigitalInOut, Direction, Pull
```
This block simply imports all the required libraries for this project.

```python
btn = DigitalInOut(board.GP2)
btn.direction = Direction.INPUT
btn.pull = Pull.UP

pixels = neopixel.NeoPixel(board.GP0, 24, brightness=1, auto_write=True, pixel_order=neopixel.GRB)
pot = analogio.AnalogIn(board.GP26)
ir_send = pulseio.PulseOut(board.GP1, frequency=38000, duty_cycle=2**15)
```
This section of the code sets up the main button to GPIO 2 as and input and pull up. The neopixel rin connected to GPIO 0, the potentiometer connected to GPIO 26, and the infrared LED connected to GPIO 1.

```python
def colourwheel(pos: int):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    # From https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
```
I'm going to be honest, I have no idea how this works, but when a value from 0-255 is provided it will output a RGB colour value.

```python
def tv_b_gone_mode():
    """
    The orginal code from this file is from https://learn.adafruit.com/circuitpython-tv-zapper-with-circuit-playground-express/gemma-m0-variant
    and has been modifed to work more effectively for the Sonic Screwdriver
    
    It was originally licensed under the MIT license by John Edgar Park for Adafruit Industries in 2018
    
    LOL, I stole this from my own GitHub repo for another project
    https://github.com/mario872/Sonic-Screwdriver
    Which was under the GPL-3.0 license
    This has been modified to work more effectively for the enviro-lamp
    
    """
    
    if btn.value: # If the button was pressed, then make sure they unpress it before starting
        while btn.value:
            if not int(round(pot.value/256)) in [256, 0, 1]:
                pixels.fill((255, 255, 255))
                time.sleep(0.1)
                pixels.fill((0, 255, 0))
                time.sleep(0.1)
    
    f = open("/codes.txt", "r") # Read the list of codes
    for line in f:
        code = eval(line)
        print(f'TV B GONE mode code sent is {code}')
        if not int(round(pot.value/256)) in [256, 0, 1]:
            pixels.fill((0, 0, 255))
        
        # If this is a repeating code, extract details
        try:
            repeat = code['repeat']
            delay = code['repeat_delay']
        except KeyError:  # By default, repeat once only!
            repeat = 1
            delay = 0
            
        # The table holds the on/off pairs
        table = code['table']
        pulses = []
        # Read through each indexed element
        for i in code['index']:
            pulses += table[i]  # And add to the list of pulses
        pulses.pop()  # Remove one final 'low' pulse

        for i in range(repeat):
            ir_send.send(array.array('H', pulses))
            time.sleep(delay)

        pixels.fill((0, 0, 0))
        time.sleep(code['delay'])

        if btn.value: # If the button was pressed, then return to the normal program
            while btn.value:
                if not int(round(pot.value/256)) in [256, 0, 1]:
                    pixels.fill((255, 255, 255))
                    time.sleep(0.1)
                    pixels.fill((0, 255, 0))
                    time.sleep(0.1)
                else:
                    pixels.fill((0, 0, 0))
                f.close()
            time.sleep(0.5)
            return
        
    f.close() 
```

Okay, so without going too in depth, this function's pure purpose is to open the `codes.txt` file, which contains ~200 different infrared patterns that have been captured from various remote controls by Adafruit in their [blog post here](https://learn.adafruit.com/circuitpython-tv-zapper-with-circuit-playground-express/gemma-m0-variant).

```python
while True:
    if not int(round(pot.value/256)) in [256, 0, 1]: # The two (+1) extreme values are reserved for white and off
        pixels.fill(colourwheel(int(round(pot.value/256)))) # The maximum pot value is 65535; divided by 256 gives you a maximum of 256,
                                                            # round that to make sure it's an integer, return that to the pixels fill function
    elif int(round(pot.value/256)) != 256: # If it's 256, then set it to full white
        pixels.fill((255, 255, 255))
    else:
        pixels.fill((0, 0, 0))

```
So, here's the main loop, which starts with the if/elif/else block.
```python
    if not int(round(pot.value/256)) in [256, 0, 1]: # The two (+1) extreme values are reserved for white and off
        pixels.fill(colourwheel(int(round(pot.value/256)))) # The maximum pot value is 65535; divided by 256 gives you a maximum of 256,
                                                            # round that to make sure it's an integer, return that to the pixels fill function

```
The first if determines if the potentiometer is between 255 and 2, in which case we use the colour wheel function to get a colour value from 0-255, this means that red is pretty hard to get using the potentiometer, but still possible.

```python
    elif int(round(pot.value/256)) != 256: # If it's 256, then set it to full white
        pixels.fill((255, 255, 255))
```

This is pretty self explanatory, if the potentiometer's value is at 256, then set the NeoPixel ring to full white.

```python
    else:
        pixels.fill((0, 0, 0))
```
Otherwise, if it's not 256, or anything between 2 and 255, then it must be 0 or 1, in which case set the colour to black / off.

```python
    if btn.value:
        time.sleep(1)
        if not btn.value:
            tv_b_gone_mode()
        else:
            while btn.value:
                pixels.deinit()
                pixels = neopixel.NeoPixel(board.GP0, 24, brightness=pot.value/65535, auto_write=True, pixel_order=neopixel.GRB)
                pixels.fill((255, 255, 255))


```
This last bit of the code checks if the button is pressed, if it is pressed, then if it's a long press (1 second), then allow the user to change the brightness of the lamp, otherwise it's a short press, in which case tv b gone mode is called.