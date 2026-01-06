# IR Receiver module for Tamagotchi protocol
# Decodes incoming IR signals into bit strings

from machine import Pin
import utime

# Hardware pins
rx_vcc = Pin(2, Pin.OUT)
signal = Pin(4, Pin.IN)

# Timing state
LAST_EDGE = utime.ticks_us()
CHANGE_LIST = []
MESSAGE_LENGTH = 0

# State machine states
LEADER_AWAITING_GAP = 1         # Last saw the long mark at the beginning
LEADER_ENDED_AWAITING_DATA = 2  # Last saw the long gap at the beginning
DATA_MARK_AWAITING_SPACE = 3    # Last saw a short mark (part of a data bit)
DATA_LONG_SPACE = 4             # Last saw a long space (represents "1" bit)
DATA_SHORT_SPACE = 5            # Last saw a short space (represents "0" bit)
waiting = 6                     # Waiting for new message to start
end_of_message = 0              # Message complete

STATE = waiting

# Timing thresholds (microseconds)
MIN_LEADER_MARK = 6000
MAX_LEADER_MARK = 12000
MIN_LEADER_GAP = 2500
MAX_LEADER_GAP = 7500
MIN_DATA_MARK = 200
MAX_DATA_MARK = 800
MIN_SHORT_DATA_GAP = 200
MAX_SHORT_DATA_GAP = 1000
MIN_LONG_DATA_GAP = MAX_SHORT_DATA_GAP
MAX_LONG_DATA_GAP = 2000
MIN_MESSAGE_END_MARK = MAX_DATA_MARK
MAX_MESSAGE_END_MARK = 1800


def enable_interrupts():
    """Enable IR receiver and start listening for signals."""
    print("Turning on IR sensor interrupts")
    signal.irq(_ir_sensor_callback_decode, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
    rx_vcc.on()


def disable_interrupts():
    """Disable IR receiver."""
    print("Turning off IR sensor interrupts")
    signal.irq(handler=None)
    rx_vcc.off()


def start_over_listening():
    """Reset state to begin listening for a new message."""
    global LAST_EDGE, STATE, MESSAGE_LENGTH, CHANGE_LIST
    STATE = waiting
    LAST_EDGE = utime.ticks_us()
    MESSAGE_LENGTH = 0
    CHANGE_LIST = []


def _ir_sensor_callback_decode(arg):
    """
    IRQ handler: decode incoming IR signal into bits.
    
    Uses a state machine to parse Tamagotchi IR protocol:
    - Leader mark (~9500us) followed by gap (~6000us)
    - Data bits: short gap = 0, long gap = 1
    - End mark signals message complete
    
    Outputs received message as: [PICO]<bits>[END]
    """
    global LAST_EDGE, STATE, MESSAGE_LENGTH, CHANGE_LIST

    new_edge = utime.ticks_us()
    run_length = utime.ticks_diff(new_edge, LAST_EDGE)
    LAST_EDGE = new_edge

    if STATE == end_of_message or STATE == waiting:
        if MIN_LEADER_MARK < run_length < MAX_LEADER_MARK and signal.value() == 1:
            STATE = LEADER_AWAITING_GAP
            MESSAGE_LENGTH = 0
        else:
            CHANGE_LIST = []
            STATE = waiting

    elif STATE == LEADER_AWAITING_GAP:
        if MIN_LEADER_GAP < run_length < MAX_LEADER_GAP:
            STATE = LEADER_ENDED_AWAITING_DATA
        else:
            CHANGE_LIST = []
            STATE = waiting

    elif STATE == LEADER_ENDED_AWAITING_DATA:
        if MIN_DATA_MARK < run_length < MAX_DATA_MARK:
            STATE = DATA_MARK_AWAITING_SPACE
        else:
            CHANGE_LIST = []
            STATE = waiting

    elif STATE == DATA_MARK_AWAITING_SPACE:
        if MIN_SHORT_DATA_GAP < run_length < MAX_SHORT_DATA_GAP:
            STATE = DATA_SHORT_SPACE
        elif MIN_LONG_DATA_GAP <= run_length < MAX_LONG_DATA_GAP:
            STATE = DATA_LONG_SPACE
        else:
            CHANGE_LIST = []
            STATE = waiting

    elif STATE == DATA_LONG_SPACE:
        if MIN_DATA_MARK < run_length < MAX_DATA_MARK:
            CHANGE_LIST.append("1")
            MESSAGE_LENGTH += 1
            STATE = DATA_MARK_AWAITING_SPACE
        elif MIN_MESSAGE_END_MARK <= run_length < MAX_MESSAGE_END_MARK:
            MESSAGE_LENGTH += 1
            CHANGE_LIST.append("1")
            print(f"[PICO]{''.join(CHANGE_LIST)}[END]")
            CHANGE_LIST = []
            STATE = end_of_message
        else:
            CHANGE_LIST = []
            STATE = waiting

    elif STATE == DATA_SHORT_SPACE:
        if MIN_DATA_MARK < run_length < MAX_DATA_MARK:
            CHANGE_LIST.append("0")
            MESSAGE_LENGTH += 1
            STATE = DATA_MARK_AWAITING_SPACE
        elif MIN_MESSAGE_END_MARK <= run_length < MAX_MESSAGE_END_MARK:
            MESSAGE_LENGTH += 1
            CHANGE_LIST.append("0")
            print(f"[PICO]{''.join(CHANGE_LIST)}[END]")
            CHANGE_LIST = []
            STATE = end_of_message
        else:
            CHANGE_LIST = []
            STATE = waiting

    else:
        CHANGE_LIST = []
        STATE = waiting
