from typing import TextIO
import sys
import time
import random
import argparse

parser = argparse.ArgumentParser(description="Simulate stress on ScyllaDB")
parser.add_argument("duration", help="Duration of stress process", type=int)
args = parser.parse_args()


def simulate_stress(stress_duration: int) -> None:
    headers = ["Throughput (ops/s)", "Latency (ms)"]
    sys.stdout.write(format_list(headers))
    start_time = time.monotonic()
    while time.monotonic() - start_time < stress_duration:
        throughput = random.randrange(0, 100000)
        latency = random.randrange(0, 20000)
        output_string = format_list([throughput, latency])
        sys.stdout.write(output_string)
        time.sleep(1)


def format_list(input_values: list) -> str:
    output = "{:<20}  {:<20}".format(input_values[0], input_values[1])
    return output + "\n"


simulate_stress(args.duration)
