from machine import UART, Pin, PWM
import struct
import time

# UART0 on GP0 (RX) and GP1 (TX)
uart = UART(0, baudrate=115200)

# Status LED
status_led = Pin(4, Pin.OUT)
status_led.value(1)
time.sleep(5)

# PWM pins for x1, y1, x2, y2
# pwm_pins = [15, 14, 13, 12]
# pwms = [PWM(Pin(p)) for p in pwm_pins]
# 
# PWM frequency
# for p in pwms:
#     p.freq(1000)
# 
# Struct format identical to Arduino struct joystick { uint8_t x1,y1,x2,y2 };
# packet_format = "BBBB"       # 4 unsigned bytes
# packet_size   = struct.calcsize(packet_format)
# 
# while True:
#     if uart.any() >= packet_size:
#         data = uart.read(packet_size)
#         if data and len(data) == packet_size:
#             x1, y1, x2, y2 = struct.unpack(packet_format, data)
# 
#             print(x1, y1, x2, y2)
# 
#             # Turn on status LED
#             status_led.value(1)
# 
#             # Convert 0–255 → 0–65k PWM duty
#             vals = [x1, y1, x2, y2]
#             for pwm, v in zip(pwms, vals):
#                 duty = int(v * 255)
#                 pwm.duty_u16(duty)
# 
#         else:
#             status_led.value(0)
# 
#     time.sleep(0.01)
# 