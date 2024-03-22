import numpy
import time
import random
import colorsys
from multiverse import Multiverse, Display
import glob
from select import select
from evdev import InputDevice

picades = glob.glob("/dev/serial/by-id/usb-Pimoroni_Picade_Max_*")

controls = map(InputDevice, ("/dev/input/event7", "/dev/input/event8"))
controls = {dev.fd: dev for dev in controls}

for dev in controls.values():
    print(dev)


# Full buffer size
WIDTH = 32
HEIGHT = 4
BYTES_PER_PIXEL = 4
BUTTON_COLOURS = [[0, 0, 0] for _ in range(14)]
PLAYER_COLOURS = [
    [255, 0, 0],
    [0, 0, 255]
]
PLAYER_MAP = [
    # Player / Button
    # Right Controls
    [1, 7],
    [1, 5],
    [1, 6],
    [1, 1],
    [1, 2],
    [1, 3],
    [1, 0],
    # Left Controls
    [0, 7],
    [0, 5],
    [0, 6],
    [0, 1],
    [0, 2],
    [0, 3],
    [0, 0]
]

display = Multiverse(
    Display(picades[0], 128, 1, 0, 0)
)

display.setup(use_threads=False)


def update():
    t = time.time() / 10.0
    for x in range(WIDTH):
        if x < 14:
            r, g, b = BUTTON_COLOURS[x]
        else:
            r, g, b = 0, 0, 0

        for y in range(HEIGHT):
            rainbow[y][x] = [b, g, r, 0]


rainbow = numpy.zeros((HEIGHT, WIDTH, BYTES_PER_PIXEL), dtype=numpy.uint8)

current_button = 0

while True:

    BUTTON_COLOURS[current_button] = [0, 255, 0]

    update()

    buf = numpy.zeros([1, 128, BYTES_PER_PIXEL], dtype=numpy.uint8)
    n = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            buf[0][n] = rainbow[y][x]
            n += 1

    # Update the displays from the buffer
    display.update(buf)

    r, w, x = select(controls, [], [])

    for fd in r:
        for event in controls[fd].read():
            if event.type == 1 and event.value == 1:
                player = controls[fd].phys.split("/")[1][5:]
                player = int(player)
                button = event.code - 304
                print(current_button, player, button)
                PLAYER_MAP[current_button] = [player, button]
                BUTTON_COLOURS[current_button] = PLAYER_COLOURS[player]
                current_button += 1
                if current_button == 14:
                    print(PLAYER_MAP)
                current_button %= 14

