# Trinamic TMC5160_BOB on Teensy 4.0 running CircuitPython

Francis Deck, 5. Oct, 2022

## Overview

This is a rudimentary driver library and test program for controlling a Trinamic TMC5160 chip as found on the TMC5160_BOB breakout board. It provides functions for setting up speed, acceleration, and coil currents, and performs absolute position moves in microsteps. I've also implemented and tested support for a quadrature rotary encoder on the BOB, but not closed loop encoder feedback.

**Do not use this project for safety critical applications**. This project has not been reviewed or approved by an engineer. The design and code are not known to be free of errors that could cause unintentional operation of motors, or hardware damage. In fact, the demo code if used as-is will run the motors spontaneously when your computer wakes up from sleep, or when the CircuitPython virtual drive is accessed.

## Project approach

My approach to embedded projects is "get coding quickly." What I mean is that I do not start with hardware design. I start with building the simplest prototype that will let me write and testing code. My rationale is that code testing will often uncover the need for hardware changes. Also, I can abandon a project before spending money on things like printed circuits and enclosures.

In this case, I left the project with the earliest prototype that worked, and have not found an application yet, that demands a more robust hardware design.

## References

Datasheets for the TMC5160 chip, and the TMC5160_BOB breakout board are found at the Trinamic website:

https://www.trinamic.com/support/eval-kits/details/tmc5160-bob/

CircuitPython for Teensy 4.0:

https://circuitpython.org/board/teensy40/

## Hardware

The schematic shows the basic wiring. The Teensy needs to be connected to a PC in order to receive power. The power supply labeled **+12 V** could be a range of voltages as indicated in the TMC5160_BOB datasheet. The current rating is determined by what motors and drive currents you're using. Make sure you use a power supply with built-in current limiting.

![Schematic diagram](./schem.png)

## Software

**tmc5160.py** is the code package that abstracts the TMC5160 functions into a class. You should include it in your project file.

**code.py** is a very simple program that will run both motors when CircuitPython starts.

## License

MIT License

Copyright (c) 2022 bassistTech

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.