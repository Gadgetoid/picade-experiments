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

picades = glob.glob("/dev/serial/by-id/usb-Pimoroni_Picade_Max_*")

EVENT = 5

controls = map(InputDevice, (f"/dev/input/event{EVENT}", f"/dev/input/event{EVENT + 1}"))
controls = {dev.fd: dev for dev in controls}


# Full buffer size
WIDTH = 32
HEIGHT = 4
BYTES_PER_PIXEL = 4

PLAYER_MAP = [
    # Player / Button
    # Right Controls
    [1, 7, (200, 0, 200)],  # R1
    [1, 5, (128, 128, 128)],    # Select
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

display = Multiverse(
    Display(picades[0], 128, 1, 0, 0)
)

display.setup(use_threads=False)


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


rainbow = numpy.zeros((HEIGHT, WIDTH, BYTES_PER_PIXEL), dtype=numpy.uint8)

attract_mode = False
last_button_press = time.time() - 60.0  # Life is short

while True:
    update()

    buf = numpy.zeros([1, 128, BYTES_PER_PIXEL], dtype=numpy.uint8)
    n = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            buf[0][n] = rainbow[y][x]
            n += 1

    # Update the displays from the buffer
    display.update(buf)

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
