import sys
import time
import random
import argparse
import csv
from typing import Iterable, Dict


def simulate_stress(stress_duration: int) -> Iterable[Dict[str, int]]:
    """
    Generates random values for throughput and latency once per second for
    a maximum of ``stress_duration`` seconds.
    """
    start_time = time.monotonic()
    while time.monotonic() - start_time < stress_duration:
        throughput = random.randrange(0, 100000)
        latency = random.randrange(0, 20000)
        row = {"Throughput (ops/s)": throughput, "Latency (ms)": latency}
        yield row
        time.sleep(1)


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(description="Simulate stress on ScyllaDB")
    parser.add_argument(
        "duration", help="Duration of stress process (integer)", type=int
    )
    args = parser.parse_args()

    if args.duration <= 0:
        parser.error("Duration must be greater than 0")

    headers = ["Throughput (ops/s)", "Latency (ms)"]
    writer = csv.DictWriter(sys.stdout, fieldnames=headers)
    writer.writeheader()
    for row in simulate_stress(stress_duration=args.duration):
        writer.writerow(row)
