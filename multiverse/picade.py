import numpy
import time
import random
import colorsys
from multiverse import Multiverse, Display
import glob

picades = glob.glob("/dev/serial/by-id/usb-Pimoroni_Picade_Max_*")

# Full buffer size
WIDTH = 32
HEIGHT = 4
BYTES_PER_PIXEL = 4
BUTTONS = [
    [255, 0, 0],
    [255, 0, 0],
    [255, 0, 0],
    [255, 0, 0],
    [255, 0, 0],
    [255, 0, 0],
    [255, 0, 0],
    [0, 0, 255],
    [0, 0, 255],
    [0, 0, 255],
    [0, 0, 255],
    [0, 0, 255],
    [0, 0, 255],
    [0, 0, 255]
]

display = Multiverse(
    Display(picades[0], 128, 1, 0, 0)
    #Display("/dev/serial/by-id/usb-Pimoroni_Picade_Max_E661410403984433-if03", 32, 4, 0, 0)
)

display.setup(use_threads=False)


def update():
    t = time.time() / 10.0
    for x in range(WIDTH):
        if x < 14:
            r, g, b = BUTTONS[x]
        else:
            r, g, b = 0, 255, 0

        for y in range(HEIGHT):
            #h = (x / WIDTH) + t
            #r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
            #rainbow[y][x] = [b, g, r, 0]
            rainbow[y][x] = [b, g, r, 0]


rainbow = numpy.zeros((HEIGHT, WIDTH, BYTES_PER_PIXEL), dtype=numpy.uint8)

# Framerate counters, don't mind these
sum_total = 0
num_frames = 0

while True:
    t_start = time.time()

    # Update the fire
    update()

    buf = numpy.zeros([1, 128, BYTES_PER_PIXEL], dtype=numpy.uint8)
    n = 0
    for x in range(WIDTH):
        for y in range(HEIGHT):
            buf[0][n] = rainbow[y][x]
            n += 1

    # Update the displays from the buffer
    display.update(buf)

    # Just FPS stuff, move along!
    t_end = time.time()
    t_total = t_end - t_start

    sum_total += t_total
    num_frames += 1

    time.sleep(1.0 / 30)

    print(buf)

    if num_frames == 60:
        print(f"Took {sum_total:.04f}s for 60 frames, {num_frames / sum_total:.02f} FPS")
        num_frames = 0
        sum_total = 0
