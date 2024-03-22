import numpy
import time
import random
import colorsys
from multiverse import Multiverse, Display
import glob
from select import select
from evdev import InputDevice
import random
import pygame

picades = glob.glob("/dev/serial/by-id/usb-Pimoroni_Picade_Max_*")

controls = map(InputDevice, ("/dev/input/event7", "/dev/input/event8"))
controls = {dev.fd: dev for dev in controls}

pygame.mixer.init(44100, -16, 1, 512)
pygame.mixer.set_num_channels(64)

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
    [1, 7, "/home/phil/Development/picade/gu-multiverse/examples/picard/explorers.mpga.wav"],
    [1, 5, "/home/phil/Development/picade/gu-multiverse/examples/picard/identify.wav"],
    [1, 6, "/home/phil/Development/picade/gu-multiverse/examples/picard/know.mpga.wav"],
    [1, 1, "/home/phil/Development/picade/gu-multiverse/examples/picard/onscreen.mpga.wav"],
    [1, 2, "/home/phil/Development/picade/gu-multiverse/examples/picard/picard.wav"],
    [1, 3, "/home/phil/Development/picade/gu-multiverse/examples/picard/plank2.wav"],
    [1, 0, "/home/phil/Development/picade/gu-multiverse/examples/picard/redalert.mpga.wav"],
    # Left Controls
    [0, 7, "drums/Cymbals/Crash/Acoustic Crash 05.wav"],
    [0, 5, "drums/Cymbals/Crash/Acoustic Crash 03.wav"],
    [0, 6, "drums/Cymbals/Crash/Acoustic Crash 01.wav"],
    [0, 1, "drums/Cymbals/Hi-Hat/Closed/Acoustic Closed Hat 42.wav"],
    [0, 2, "drums/Cymbals/Crash/Acoustic Crash Damped 34.wav"],
    [0, 3, "drums/Cymbals/Crash/Acoustic Crash Gong 01.wav"],
    [0, 0, "drums/Cymbals/Crash/Acoustic Crash Ride 03.wav"]
]

for n, p in enumerate(PLAYER_MAP):
    if p[2]:
        p[2] = pygame.mixer.Sound(p[2])
        p.append(pygame.mixer.Channel(n))


def find_sample(player, button):
    for (current_player, current_button, sample, channel) in PLAYER_MAP:
        if player == current_player and button == current_button and sample:
            return sample, channel
    return None, None


display = Multiverse(
    Display(picades[0], 128, 1, 0, 0)
)

display.setup(use_threads=False)


def update():
    t = time.time() / 10.0
    rainbow[:] *= 0.99


def set_button_leds(player, button, r, g, b):
    for x, (current_player, current_button, _, _) in enumerate(PLAYER_MAP):
        if player == current_player and button == current_button:
            for y in range(4):
                rainbow[y][x] = [b, g, r, 0]


rainbow = numpy.zeros((HEIGHT, WIDTH, BYTES_PER_PIXEL), dtype=numpy.float32)

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
            buf[0][n] = rainbow[y][x].astype(numpy.uint8)
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
                #print(current_button, player, button)

                sample, channel = find_sample(player, button)
                if sample is not None:
                    channel.play(sample, loops=0)
                    set_button_leds(player, button, *PLAYER_COLOURS[player])
