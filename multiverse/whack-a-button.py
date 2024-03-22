import numpy
import time
import random
import colorsys
from multiverse import Multiverse, Display
import glob
from select import select
from evdev import InputDevice
import random

picades = glob.glob("/dev/serial/by-id/usb-Pimoroni_Picade_Max_*")

controls = map(InputDevice, ("/dev/input/event7", "/dev/input/event8"))
controls = {dev.fd: dev for dev in controls}


# Full buffer size
WIDTH = 32
HEIGHT = 4
BYTES_PER_PIXEL = 4
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
        if current_button is not None and current_button == x:
            player = PLAYER_MAP[current_button][0]
            r, g, b = PLAYER_COLOURS[player]
        else:
            r, g, b = 0, 0, 0

        for y in range(HEIGHT):
            rainbow[y][x] = [b, g, r, 0]


rainbow = numpy.zeros((HEIGHT, WIDTH, BYTES_PER_PIXEL), dtype=numpy.uint8)

current_button = None
mistakes = 0
correct = 0

t_start = time.time()

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

    r, w, x = select(controls, [], [])

    for fd in r:
        for event in controls[fd].read():
            if event.type == 1 and event.value == 1:
                player = controls[fd].phys.split("/")[1][5:]
                player = int(player)
                button = event.code - 304
                #print(current_button, player, button)

                if current_button is not None:
                    want_player, want_button = PLAYER_MAP[current_button]
                    if want_player == player and want_button == button:
                        old_button = current_button
                        correct += 1
                        # Lazy way to make sure our next button is different
                        while current_button == old_button:
                            current_button = random.randint(0, len(PLAYER_MAP) - 1)
                    else:
                        mistakes += 1
                elif button == 4:
                    current_button = random.randint(0, len(PLAYER_MAP) - 1)

    t = time.time() - t_start
    freq = correct / t
    print(f"{mistakes} mistakes, {correct} hit, {freq}/sec")
