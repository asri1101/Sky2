from machine import Pin, SPI
from time import sleep
from nrf24l01 import NRF24L01
import struct 

# pin wiring
led = Pin(1, Pin.OUT)
spi = SPI(0, sck = 2, mosi = 3, miso = 4, baudrate = 100000)
ce = Pin(5, Pin.OUT, value = 0)
csn = Pin(6, Pin.OUT, value = 1)
nrf = NRF24L01(spi, csn, ce, payload_size=8)

# set receiver address for transmitter and start listening for any signals 
nrf.open_rx_pipe(1, b'\xe1\xf0\xf0\xf0\xf0')
nrf.start_listening()
while True:
    led.value(0)
    if nrf.any():
        while nrf.any():
            data = nrf.recv()
            #.decode('utf-8', 'ignore').strip() # throws unicode error
        # once data is received, read it 
        x, y, z = struct.unpack("HHH", data[:6]) # unpacks data into respective values 
        print(f"x={x},y={y}, z={z}")
        led.value(1)
        sleep(0.01)