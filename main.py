# Tamagotchi-in-the-middle: IR badge that can impersonate a Tamagotchi
# or send PixMob IR commands

from machine import Pin
import neopixel
import utime
import rx
import converters
from ir_tx import Player

# Pin configuration
ir_pin = Pin(7, Pin.OUT, value=0)
button_mode = Pin(27, Pin.IN, Pin.PULL_UP)
button_a = Pin(28, Pin.IN, Pin.PULL_UP)
button_b = Pin(29, Pin.IN, Pin.PULL_UP)
button_c = Pin(6, Pin.IN, Pin.PULL_UP)

# Built-in NeoPixel LED
built_in_led_power = Pin(11, Pin.OUT)
built_in_led_power.value(1)
built_in_led_data = neopixel.NeoPixel(Pin(12), 1)

# Configuration
READ_FROM_SERIAL_INSTEAD_OF_BUTTON = False
LISTEN_TIMEOUT_MS = 1000
CURRENT_MODE = "tamagotchi"

# Tamagotchi visit message pairs (each visit requires 2 messages)
VISIT_1_MSG_A1 = "0000111000000000001100011011111000011110000000110000000000001101000010001010000000000010000000000010001000000000000000000000000000000000000000000001010000001011"
VISIT_1_MSG_A2 = "0000111000001000001100011011111000011110000000110000000000001101000010001010000000000001000000000000000000000000000000000000000000000000000000000000000011011100"

VISIT_2_MSG_A1 = "0000111000000000110111100101101000110010100010001000100010001000100010001000100000000010000000000010001100000000000001100000000000000000000000000000101001010101"
VISIT_2_MSG_A2 = "0000111000001000110111100101101000110010100010001000100010001000100010001000100000000011000000000000000000000000000000000000000000000000000000000000000000101011"

VISIT_3_MSG_A1 = "0000111000000000110111100101101000110010100010001000100010001000100010001000100000000010000000000010001100000000000001100000000000000000000000000001111001101001"
VISIT_3_MSG_A2 = "0000111000001000110111100101101000110010100010001000100010001000100010001000100000000000000000000000000000000000000000000000000000000000000000000000000000101000"

# PixMob IR pulse patterns (timing in microseconds)
PIXMOB_RED = [1400, 1400, 700, 700, 700, 1400, 700, 2800, 700, 2100, 1400, 700, 700, 700, 700, 1400, 1400, 2800, 1400, 2800, 700]
PIXMOB_GREEN = [700, 700, 700, 2100, 1400, 700, 700, 2800, 700, 1400, 700, 700, 700, 1400, 1400, 700, 700, 1400, 700, 700, 700, 700, 700, 700, 700, 2100, 700]
PIXMOB_BLUE = [1400, 1400, 700, 700, 700, 700, 1400, 2800, 700, 1400, 700, 1400, 700, 1400, 700, 1400, 1400, 2800, 1400, 2800, 700]


def set_built_in_led_color(color):
    """Set the built-in NeoPixel to an RGB color tuple."""
    built_in_led_data[0] = color
    built_in_led_data.write()
    utime.sleep_ms(1)


def wait_for_single_message():
    """Wait for an IR message to be received, with timeout."""
    start = utime.ticks_ms()
    while True:
        utime.sleep(0.001)
        if utime.ticks_diff(utime.ticks_ms(), start) > LISTEN_TIMEOUT_MS:
            print("[PICO]timed out[END]")
            break
        if rx.STATE == rx.end_of_message:
            break

    if rx.STATE == rx.end_of_message:
        rx.STATE = rx.waiting
        return True
    return False


def send_message_and_wait_for_response(message_to_send, retries=1):
    """Send a Tamagotchi IR message and wait for a response."""
    rx.disable_interrupts()
    print("starting play")
    rx.start_over_listening()

    try:
        lengths = converters.to_lengths(message_to_send)
        ir_out = Player(ir_pin, asize=len(lengths) + 1, verbose=True)
        ir_out.play(lengths)
        print(len(lengths))
        utime.sleep_us(sum(lengths))
    except:
        print("Error sending")
        return False

    rx.enable_interrupts()
    got_response = wait_for_single_message()

    if got_response:
        print("Got response!")
        return True
    elif retries > 0:
        print("Failed to receive response, retrying send")
        return send_message_and_wait_for_response(message_to_send, retries - 1)
    else:
        print("Failed to receive response, no retries left")
        return False


def perform_exchange(messages_to_send):
    """Perform a full Tamagotchi visit exchange (multiple messages)."""
    rx.disable_interrupts()
    led_states = [(10, 0, 0), (20, 0, 0), (15, 5, 5), (10, 10, 5),
                  (5, 15, 5), (0, 15, 10), (0, 10, 15), (0, 5, 20)]

    for ind, message_to_send in enumerate(messages_to_send):
        set_built_in_led_color(led_states[ind % len(led_states)])
        retries = 2 if ind == 0 else 1
        success = send_message_and_wait_for_response(message_to_send, retries=retries)
        if not success:
            return False

    print("Successful exchange!")
    return True


def transmit_arbitrary_blocking(lengths):
    """Transmit arbitrary IR pulse lengths (for PixMob)."""
    rx.disable_interrupts()
    sender = Player(ir_pin, asize=len(lengths) + 1, verbose=True)
    sender.play(lengths)
    print(len(lengths))
    utime.sleep_us(sum(lengths))
    rx.enable_interrupts()


# Main loop
set_built_in_led_color((5, 10, 0))

while True:
    action = None

    if READ_FROM_SERIAL_INSTEAD_OF_BUTTON:
        action = input().lower()
    else:
        # Check for button presses based on current mode
        if CURRENT_MODE == "tamagotchi":
            if button_a.value() == 0:
                print("Button A pressed")
                action = "visit1"
            elif button_b.value() == 0:
                print("Button B pressed")
                action = "visit2"
            elif button_c.value() == 0:
                print("Button C pressed")
                action = "visit3"
        elif CURRENT_MODE == "pixmob":
            if button_a.value() == 0:
                print("Button A pressed")
                action = "pixmobRed"
            elif button_b.value() == 0:
                print("Button B pressed")
                action = "pixmobGreen"
            elif button_c.value() == 0:
                print("Button C pressed")
                action = "pixmobBlue"

        # Mode switch button
        if button_mode.value() == 0:
            if CURRENT_MODE == "tamagotchi":
                CURRENT_MODE = "pixmob"
                set_built_in_led_color((0, 5, 10))
            else:
                CURRENT_MODE = "tamagotchi"
                set_built_in_led_color((5, 10, 0))
            utime.sleep_ms(300)

    # Handle actions
    if action:
        print(action)
        if action == "visit1":
            perform_exchange([VISIT_1_MSG_A1, VISIT_1_MSG_A2])
        elif action == "visit2":
            perform_exchange([VISIT_2_MSG_A1, VISIT_2_MSG_A2])
        elif action == "visit3":
            perform_exchange([VISIT_3_MSG_A1, VISIT_3_MSG_A2])
        elif action == "pixmobRed":
            transmit_arbitrary_blocking(PIXMOB_RED)
        elif action == "pixmobGreen":
            transmit_arbitrary_blocking(PIXMOB_GREEN)
        elif action == "pixmobBlue":
            transmit_arbitrary_blocking(PIXMOB_BLUE)
        else:
            print(f"Invalid action: {action}")

    # Update LED to show current mode
    if CURRENT_MODE == "pixmob":
        set_built_in_led_color((0, 5, 10))
    else:
        set_built_in_led_color((5, 10, 0))

    utime.sleep_ms(50)
