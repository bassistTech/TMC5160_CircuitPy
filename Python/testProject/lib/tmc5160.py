'''
Trinamic TMC5160_BOB driver
Francis Deck, 5. Oct 2022

Bare bones driver for Trinamic TMC5160 breakout board and optional encoder
Tested on Teensy 4.0, with these hookups:

Teensy 4.0      TMC5160_BOB    Encoder  Power
Gnd             GND
3.3V            VCC_IO
CS (pin 10)     CSN
MOSI (pin 11)   SDI
MISO (pin 12)   SDO
SCK (pin 13)    SCK
                DRV_ENN = Jumper to ground on board
                CLK16 = Jumper to ground on board
                VS                     +12 V
                GND                    GND
                ENCA ---r10k--- A
                ENCN ---r10k--- B
                ENCN ---r10k--- X
                GND             G
VS (USB 5V)                     5V

The r10k's are series resistors, to handle 5 to 3.3 V compatibility between
the encoder and the Teensy. A properly designed circuit would use a real
level shifter chip. Encoder is optional and can be omitted.

I started with example code from Trinamic, and translated to Python
https://blog.trinamic.com/2017/04/05/how-to-use-tmc5130-eval-with-your-arduino-mega/

When given options for chip features, I chose the simplest or most basic.
'''

import board
import digitalio
import time

# Constants from the TMC5160 datasheet, there are many more
# write and read bits
WRITE = const(0x80)
READ = const(0)
# chip registers
GSTAT = const(1)
GCONF = const(0)
CHOPCONF = const(0x6C)
IHOLD_IRUN = const(0x10)
TPOWERDOWN = const(0x11)
PWM_CONF = const(0x70)
A1 = const(0x24)
V1 = const(0x25)
AMAX = const(0x26)
VMAX = const(0x27)
D1 = const(0x2A)
VSTOP = const(0x2B)
RAMPMODE = const(0x20)
XACTUAL = const(0x21)
XTARGET = const(0x2D)
X_ENC = const(0x39)
# status byte bits
STATUS_STOP_R = const(7)
STATUS_STOP_L = const(6)
POSITION_REACHED = const(5)
VELOCITY_REACHED = const(4)
STANDSTILL = const(3)
SG2 = const(2)
DRIVER_ERROR = const(1)
RESET_FLAG = const(0)

class TMC5160():
    def __init__(self, spi, csPin):
        '''
        spi = pre-initialized SPI bus
        csPin = chip select pin
        '''
        self.verbose = False
        self.cs = digitalio.DigitalInOut(csPin)
        self.cs.direction = digitalio.Direction.OUTPUT
        self.cs.value = True
        self.spi = spi
        self.x = bytearray(5) # outgoing data buffer
        self.y = bytearray(5) # incoming data buffer
        self.flags = bytearray(8)

    def send(self, rw, addr, data):
        '''
        rw = WRITE or READ
        addr = address, 0 to 0x7F
        data = 32 bit integer data
        returns: 32 bit integer result
        '''
        # Convert negative number to 2's complement
        if data < 0:
            data = (2<<31) + data
        # Command byte
        self.x[0] = rw + addr
        # Data payload
        for i in range(4):
            self.x[4 - i] = data % 256
            data = data // 256
        # Perform the transaction
        self.cs.value = False
        self.spi.write_readinto(self.x, self.y)
        self.cs.value = True
        # Unpack the flag bits
        fsum = self.y[0]
        for i in range(8):
            self.flags[i] = fsum % 2
            fsum = fsum // 2
        if self.verbose:
            print(rw, addr, "{0:b}".format(self.y[0]),
                "{0:b}".format(fsum))

    def read(self, addr):
        '''
        addr = 7 bit register address
        '''
        # need two read's, one to collect the data, one to transfer it back
        self.send(READ, addr, 0)
        self.send(READ, addr, 0)
        # convert bytes to integer
        sum = 0
        for i in range(1, 5):
            sum = sum*256 + self.y[i]
        # convert two's complement to signed integer
        if sum > (2<<30):
            sum = sum - (2<<31)
        return sum

    def setup(self, speed, taccel, irun, ihold):
        '''
        speed = microsteps per second
        taccel = acceleration time in seconds
        irun = run current in mA
        ihold = hold current in mA
        '''
        self.send(WRITE, GCONF, 0)
        # CHOPCONF: TOFF=5, HSTRT=5, HEND=3, TBL=2, CHM=0 (spreadcycle)
        self.send(WRITE, CHOPCONF, 0x000101D5)
        # run current constant
        ir = int(irun*31/3100 + 0.5)
        if ir > 31:
            ir = 31
        elif ir < 1:
            ir = 1
        # hold current constant
        ih = int(ihold*31/3100 + 0.5)
        if ih > 31:
            ih = 31
        elif ih < 1:
            ih = 1
        # hold & run current as a single binary block
        ihir = 0x70000 + 0x100*ir + ih
        self.send(WRITE, IHOLD_IRUN, ihir)
        self.send(WRITE, TPOWERDOWN, 10)
        # PWM_CONF: AUTO=1, 2/1024 Fclk, Switch amp limit=200, grad=1
        self.send(WRITE, PWM_CONF, 0)
        a = int(speed/taccel*0.01527 + 0.5)
        v = int(speed*1.3981 + 0.5)
        self.send(WRITE, A1, a)
        self.send(WRITE, V1, v)
        self.send(WRITE, AMAX, a)
        self.send(WRITE, VMAX, v)
        self.send(WRITE, D1, a) # deceleration
        self.send(WRITE, VSTOP, 10)
        self.send(WRITE, RAMPMODE, 0)
        self.send(WRITE, XACTUAL, 0)
        self.send(WRITE, XTARGET, 0)

    def moveAbsolute(self, x, wait4 = True):
        '''
        Move to absolute position
        x = microsteps
        wait4 = True if wait for move to be done before returning
        '''
        self.send(WRITE, XTARGET, x) # sendData(0xAD, x)
        self.send(READ, XACTUAL, 0) # sendData(0x21, 0)
        # Loop til target position is reached
        while wait4:
            self.send(READ, XACTUAL, 0)
            if self.flags[POSITION_REACHED] == 1:
                break
            if self.flags[DRIVER_ERROR] == 1:
                print('Driver error')
                break
            time.sleep(0.1)
            pass
            
    def getPosition(self):
        return self.read(XACTUAL)
        
    def setPosition(self, x):
        self.send(WRITE, XACTUAL, 0)
        self.send(WRITE, XTARGET, 0)

    def readEncoder(self):
        '''
        Read the position encoder if installed
        returns: encoder counts
        '''
        return self.read(X_ENC)
        # self.send(READ, X_ENC, 0)
        # return self.send(READ, X_ENC, 0)

    def setEncoder(self, x):
        '''
        Set the encoder to a given number of counts
        x = encoder counts
        '''
        self.send(WRITE, X_ENC, int(x + 0.5))