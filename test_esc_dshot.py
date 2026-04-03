# Author: Bekhruz Malikov
import rp2
import machine
from machine import Pin
import time

################################################################
### @rp2.asm_pio(...) takes the Python function defined,
### wraps it with a decorator, and converts it into a low-level
### PIO program that the RP2040 can run directly on its hardware
### state machine, helpful for sending packets to the ESC ###
################################################################

@rp2.asm_pio(
    out_shiftdir=rp2.PIO.SHIFT_LEFT, #Read bits left to right (MSB first) — DShot requires this
    autopull=False, # don't grab data yet 
    set_init=rp2.PIO.OUT_LOW, # SET pin starts LOW
    out_init=rp2.PIO.OUT_LOW, # The OUTPUT pin starts LOW
    sideset_init=rp2.PIO.OUT_LOW # Signal wire to ESC starts LOW
    )

# sequence of moving bits from Pico to ESC 
def dshot():
    # ESC signal must stay low during fetching of bits from CPU
    pull(noblock).side(0)
    set(x, 15).side(0)
    label("bitloop")
    out(y,1)
        
   
# helpers for making the packets of bits for throttle 
def make_packet(throttle, telemetry=False):
    packet = (throttle << 1) | (1 if telemetry else 0)
    break

# use the packet of bits and read them using an FSM 

#####################################
####    REFERENCES (PIO)          ###
####   Assembly instructions      ###
#####################################

# Instruction  | What it does
# -------------|--------------------------------------------------------------
# pull         | Fetches the next packet from Python into the PIO holding buffer (FIFO)
# noblock      | Modifier for pull - reuse last packet if no new one is ready
# .side(0)     | Simultaneously sets ESC signal wire LOW during the instruction
# .side(1)     | Simultaneously sets ESC signal wire HIGH during the instruction
# jmp          | Jump to a label, can be conditional e.g. jmp(not_y, "zero")
# nop          | No Operation - waste exactly one clock cycle to control timing
# label        | Marks a named spot in code that jmp can jump back to
# set          | Load a number into a register e.g. set(x, 15) sets counter to 15
# out          | Shift bits from holding buffer into a register e.g. out(y, 1)

# Functions: 
    # dshot()
        # is the middleman toolchain that:
        # Pulls the packet out of the CPU queue
        # Breaks it apart bit by bit
        # Translates each bit into precise electrical HIGH/LOW timing on the wire
        # Repeats until all 16 bits are delivered


# Visuals:
    # Visual 1.1
        # 1. Pull 16-bit packet from CPU queue
           # ↓
        # 2. If no new packet, reuse last one
            # ↓
        # 3. Set counter to 15 (will count down to 0 = 16 bits total)
           #  ↓
        # 4. Pull ESC wire HIGH (start of bit)
           #  ↓
        # 5. Shift 1 bit into Y register
           #  ↓
        # 6. Was that bit a 1 or 0?
           #   /        \
        #   bit=1       bit=0
       #   stay HIGH   go LOW
       #   longer      sooner
       #      \        /
       # 7. Counter - 1, loop back to step 4
           #     ↓
        # 8. Counter hit 0? All 16 bits sent → done
    # Visual 1.2

# Terminology
    # CRC
        # stands for Cyclic Redundancy Check— it's a checksum, basically a fingerprint of your packet.
        # prevents making corrupted packets of data, so a unique fingerprint is assigned
    # Telemetry
        # a request flag to send back all data about motors
    # ^
        # XOR operation: Exclusive OR
        # Output is 1 if the bits are DIFFERENT, 0 if they are the SAME

# Important Explanations
    # 1. This means if the ESC receives the packet and XORs the same chunks together,
    # it should get the same CRC fingerprint back. If even one bit changed during
    # transmission, the fingerprint won't match and the ESC knows something went wrong.

