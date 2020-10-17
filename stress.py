from typing import TextIO
import sys
import time
import random
import argparse
import csv

parser = argparse.ArgumentParser(description="Simulate stress on ScyllaDB")
parser.add_argument("duration", help="Duration of stress process", type=int)
args = parser.parse_args()


def simulate_stress(stress_duration: int) -> None:
    headers = ["Throughput (ops/s)", "Latency (ms)"]
    start_time = time.monotonic()
    writer = csv.DictWriter(sys.stdout, fieldnames=headers)
    writer.writeheader()

    while time.monotonic() - start_time < stress_duration:
        throughput = random.randrange(0, 100000)
        latency = random.randrange(0, 20000)
        row = {"Throughput (ops/s)": throughput, "Latency (ms)": latency}
        writer.writerow(row)
        time.sleep(1)


simulate_stress(args.duration)
