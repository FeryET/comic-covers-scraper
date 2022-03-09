import math
import datetime


def progress(sequence, interval=0.01):
    interval = math.ceil(interval * len(sequence))
    for idx, item in enumerate(sequence):
        if idx != 0 and idx % interval == 0:
            print(
                f"{datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}\tProgress"
                f" currently at {100 * (idx / len(sequence)):.2f}%."
            )
        yield item
