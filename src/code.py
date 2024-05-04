"""
Copyright (C) 2024  James Glynn

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You did not receive a copy of the GNU General Public License
along with this program. Please see https://www.gnu.org/licenses/gpl-3.0.html.
"""

import time, board, neopixel, analogio, pulseio, array
from digitalio import DigitalInOut, Direction, Pull

btn = DigitalInOut(board.GP2)
btn.direction = Direction.INPUT
btn.pull = Pull.UP

pixels = neopixel.NeoPixel(board.GP0, 24, brightness=1, auto_write=True, pixel_order=neopixel.GRB)
pot = analogio.AnalogIn(board.GP26)
ir_send = pulseio.PulseOut(board.GP1, frequency=38000, duty_cycle=2**15)

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

while True:
    if not int(round(pot.value/256)) in [256, 0, 1]: # The two (+1) extreme values are reserved for white and off
        pixels.fill(colourwheel(int(round(pot.value/256)))) # The maximum pot value is 65535; divided by 256 gives you a maximum of 256,
                                                            # round that to make sure it's an integer, return that to the pixels fill function
    elif not int(round(pot.value/256)) in [256, 255]: # If it's 256, then 11
        pixels.fill((255, 255, 255))
    else:
        pixels.fill((0, 0, 0))
        
    if btn.value:
        time.sleep(1)
        if not btn.value:
            tv_b_gone_mode()
        else:
            while btn.value:
                pixels.deinit()
                pixels = neopixel.NeoPixel(board.GP0, 24, brightness=pot.value/65535, auto_write=True, pixel_order=neopixel.GRB)
                pixels.fill((255, 255, 255))

