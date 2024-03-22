import numpy
import time
import math
import random
import colorsys
from multiverse import Multiverse, Display
import glob
from select import select
from evdev import InputDevice
import random
from colorsys import hsv_to_rgb

BRIGHTNESS = 0.6

# Full buffer size
WIDTH = 32
HEIGHT = 4
BYTES_PER_PIXEL = 4

PLAYER_MAP = [
    # Player / Button / (R, G, B)
    # Right Controls
    [1, 7, (200, 0, 200)],    # R1
    [1, 5, (128, 128, 128)],  # Select
    [1, 6, (0, 200, 200)],    # L1
    [1, 1, (255, 0, 0)],      # B
    [1, 2, (0, 0, 255)],      # X
    [1, 3, (200, 200, 0)],    # Y
    [1, 0, (0, 255, 0)],      # A
    # Left Controls
    [0, 7, (200, 0, 200)],  # R1
    [0, 5, (128, 128, 128)],    # Select
    [0, 6, (0, 200, 200)],    # L1
    [0, 1, (255, 0, 0)],      # B
    [0, 2, (0, 0, 255)],      # X
    [0, 3, (200, 200, 0)],    # Y
    [0, 0, (0, 255, 0)]       # A
]

# For Multiverse display output
picades = glob.glob("/dev/serial/by-id/usb-Pimoroni_Picade_Max_*")
cosmic = glob.glob("/dev/serial/by-id/usb-Pimoroni_Multiverse_*")

# Joystick event device
# Player two's joystick has an -if01- in the path
players = glob.glob("/dev/input/by-id/usb-Pimoroni_Picade_Max_*-event-joystick")
player1 = [player for player in players if "-if01-" not in player][0]
player2 = [player for player in players if "-if01-" in player][0]

controls = map(InputDevice, (player1, player2))
controls = {dev.fd: dev for dev in controls}

display = Multiverse(
    Display(picades[0], 128, 1, 0, 0)
)

display.setup(use_threads=False)

rear_leds = Multiverse(
    Display(cosmic[0], 32, 32, 0, 0)
)

rear_leds.setup(use_threads=False)


def update():
    for x in range(WIDTH):
        t = (math.sin(time.time() + x * 2.0) + 1) / 2.0
        if x < 14:
            r, g, b = PLAYER_MAP[x][2]
        else:
            r, g, b = 0, 0, 0

        if attract_mode:
            f = t % 1
            r, g, b = [int(c * f) for c in (r, g, b)]

        rainbow[0][x] = [b, g, r, 0]
        rainbow[1][x] = [b, g, r, 0]
        rainbow[2][x] = [b, g, r, 0]
        rainbow[3][x] = [b, g, r, 0]

    h_o = time.time() / 10
    for x in range(32):
        h = (int(x / 2) * 2) / 32.0
        for y in range(32):
            r, g, b = [int(c * 255) for c in hsv_to_rgb(h + h_o, 1.0, 1.0)]
            cosmic_buffer[x][y] = [r, g, b, 0]


rainbow = numpy.zeros((HEIGHT, WIDTH, BYTES_PER_PIXEL), dtype=numpy.uint8)
cosmic_buffer = numpy.zeros((32, 32, 4), dtype=numpy.uint8)
cosmic_buffer[:][:] = [255, 0, 0, 0]

attract_mode = False
last_button_press = time.time() - 60.0  # Life is short

while True:
    update()

    buf = numpy.zeros([1, 128, BYTES_PER_PIXEL], dtype=numpy.uint8)
    n = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            buf[0][n] = rainbow[y][x] * BRIGHTNESS
            n += 1

    # Update the displays from the buffer
    display.update(buf)
    rear_leds.update(cosmic_buffer)

    r, w, x = select(controls, [], [], 0)

    for fd in r:
        for event in controls[fd].read():
            if event.type == 1 and event.value == 1:
                player = controls[fd].phys.split("/")[1][5:]
                player = int(player)
                button = event.code - 304
                print(player, button)

                last_button_press = time.time()
            elif event.type == 3 and event.value != 0:
                last_button_press = time.time()

    attract_mode = time.time() - last_button_press > 60

    time.sleep(1.0 / 30)
