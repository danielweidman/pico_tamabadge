# Pico TamaBadge

A Defcon-style [SAO (Simple Add-On)](https://hackaday.com/2024/09/26/an-ode-to-the-sao/) badge that can interact with the 2024-25 Tamagotchi Connection rerelease. Press a button to trigger a "visit" with any nearby Tamagotchi!

Also doubles as a [PixMob IR transmitter for controlling LED wristbands](https://github.com/danielweidman/pixmob-ir-reverse-engineering).

<img src="https://github.com/user-attachments/assets/3e465a2f-8051-4976-8cf5-2d73ed727d56" alt="PXL_20250803_224831185" width="400">


## Credits

**This project is built on top of significant reverse-engineering work**

- **[Zach Resmer's Tamagometer](https://github.com/zacharesmer/tamagometer)** — The core protocol reverse-engineering that makes this work. Zach figured out the Tamagotchi IR protocol, message formats, and documented everything needed to communicate with the 2024-25 Tamagotchi Connection. Go check out his repo for all the technical details + the Tamagometer web app for interacting with Tamagotchis in-depth!

- **[Peter Hinch's micropython_ir](https://github.com/peterhinch/micropython_ir)** — The IR transmission library used for transmitting arbitrary IR data.

## Hardware

- SEED Xiao RP2040
- IR LED (connected to GPIO 7)
- IR receiver module (VCC on GPIO 2, signal on GPIO 4)
- 3 buttons for actions (GPIO 28, 29, 6)
- 1 button for mode switch (GPIO 27)
- Built-in NeoPixel LED (power on GPIO 11, data on GPIO 12)

KiCad project files and production-ready gerbers are available in the `hardware/` folder.

### Tamagotchi Mode (green LED)
- **Button A** — Trigger Visit 1
- **Button B** — Trigger Visit 2  
- **Button C** — Trigger Visit 3

Point the badge at your Tamagotchi and press a button. The badge will send the visit message and wait for a response.

### PixMob Mode (blue LED)
Press the mode button to switch. Buttons A/B/C send red/green/blue IR commands.

## File Structure

```
pico_tamabadge/
├── main.py          # Main application loop
├── rx.py            # IR receiver & Tamagotchi protocol decoder
├── converters.py    # Bit string <-> IR timing conversion
├── ir_tx/
│   ├── __init__.py  # IR transmitter (Player class)
│   └── rp2_rmt.py   # RP2040 PIO-based pulse generation
└── hardware/
    ├── kicad/                    # KiCad project files
    └── gerbers/                  # Production-ready files
```
