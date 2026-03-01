from machine import Pin, SPI
from time import sleep
from nrf24l01 import NRF24L01

led = Pin(1, Pin.OUT)
spi = SPI(0, sck = 2, mosi = 3, miso = 4, baudrate = 100000)
ce = Pin(6, Pin.OUT, value = 0)
csn = Pin(5, Pin.OUT, value = 1)
nrf = NRF24L01(spi, csn, ce, payload_size=8)

nrf.open_tx_pipe(b'\xe1\xf0\xf0\xf0\xf0')
while True:
    try:
        print("Sending")
        nrf.send(b'50495148')
    except OSError as e:
        print(e)
    led.value(1)
    sleep(0.01)
    led.value(0)
    sleep(0.04)
