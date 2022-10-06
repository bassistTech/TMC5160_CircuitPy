'''
Test program for TMC5160_BOB on Teensy 4.0 running CircuitPython
Francis Deck, 5 Oct 2022
'''

import board
import analogio
import busio

import tmc5160

spi = busio.SPI(board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Lock SPI bus permanently, no other program will try using it

while not spi.try_lock():
    pass

# Tried 5
spi.configure(baudrate=3000000, phase = 0, polarity = 0)
x = tmc5160.TMC5160(spi, board.D10)
y = tmc5160.TMC5160(spi, board.D9)
x.setup(102400, 0.25, 250, 125)
y.setup(102400, 0.25, 250, 125)

x.moveAbsolute(102400)
x.moveAbsolute(-51200)

y.moveAbsolute(102400)
y.moveAbsolute(-51200)