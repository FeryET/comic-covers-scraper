import math


def progress(sequence, interval=0.01):
    interval = math.ceil(interval * len(sequence))
    for idx, item in enumerate(sequence):
        if idx != 0 and idx % interval == 0:
            print(f"Currently at {100 * (idx / len(sequence)):.2f}%.")
        yield item
