import board
import busio
import tmc5160

spi = busio.SPI(board.SCK, MISO=board.MISO, MOSI=board.MOSI)

while not spi.try_lock():
    pass

spi.configure(baudrate=3000000, phase = 0, polarity = 0)

x = tmc5160.TMC5160(spi, board.D10)
y = tmc5160.TMC5160(spi, board.D9)

x.setup(102400, 0.25, 250, 125)
y.setup(102400, 0.25, 250, 125)

print('configured motors')