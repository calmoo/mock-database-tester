import argparse
import csv
import datetime
import io
import random
import subprocess
import textwrap
import time
from statistics import mean, quantiles
from threading import Thread
from typing import Dict, List


class ProcessStats:
    """
    Details of a process.

    Total time is separate from start time and end time because there could be
    system clock changes while running the process.
    """
    def __init__(
        self, pid: int, start_time: float, end_time: float, total_time: float
    ):
        self.pid = pid
        self.start_time = start_time
        self.end_time = end_time
        self.total_time = total_time


class StressTest:
    def _stress_test(self, duration: int, shared_dict: dict) -> None:
        """
        This creates a thread which runs ``stress.py``.
        It runs this thread for ``duration`` seconds.

        It captures the standard output of this thread and stores data from
        this in the given ``shared_dict``.
        """

        start_time = time.time()
        start_time_monotonic = time.monotonic()

        stress_test_process = subprocess.Popen(
            ["python", "stress.py", str(duration)],
            stdout=subprocess.PIPE,
        )
        output_bytes = stress_test_process.communicate()[0]
        output_string = output_bytes.decode()
        output_file = io.StringIO(output_string)
        csv_reader = csv.DictReader(output_file)
        rows = [row for row in csv_reader]
        throughput_values_int = [
            int(row["Throughput (ops/s)"]) for row in rows
        ]
        latency_values_int = [int(row["Latency (ms)"]) for row in rows]
        end_time = time.time()
        end_time_monotonic = time.monotonic()
        total_time = end_time_monotonic - start_time_monotonic
        pid = stress_test_process.pid
        process_stats = ProcessStats(
            pid=pid,
            start_time=start_time,
            end_time=end_time,
            total_time=total_time,
        )
        shared_dict["throughput"].extend(throughput_values_int)
        shared_dict["latency"].extend(latency_values_int)
        shared_dict["execution_stats"].append(process_stats)

    def run(self, num_threads: int) -> "Metrics":
        """
        Runs the stress function in ``num_threads`` threads.

        Each thread is given a unique duration which is between 1 and the given
        ``num_threads``.

        A shared dictionary is used amongst all spawned threads.
        """
        shared_dict: Dict[str, List] = {
            "throughput": [],
            "latency": [],
            "execution_stats": [],
        }
        threads = []
        duration_list = random.sample(range(2, num_threads + 2), num_threads)
        for duration in duration_list:
            thread = Thread(
                target=self._stress_test, args=(duration, shared_dict)
            )
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

        return Metrics(
            throughput_metrics=shared_dict["throughput"],
            latency_metrics=shared_dict["latency"],
            execution_metrics=shared_dict["execution_stats"],
        )


class Metrics:
    """
    This class takes all of the simulated values and execution metrics
    from all of the threads run, and calculates various statistics based
    on those values.
    """

    def __init__(
        self,
        throughput_metrics: List[int],
        latency_metrics: List[int],
        execution_metrics: List[ProcessStats],
    ):
        self.average_throughput = mean(throughput_metrics)
        self.average_latency = mean(latency_metrics)
        self.max_throughput = max(throughput_metrics)
        self.max_latency = max(latency_metrics)
        self.min_throughput = min(throughput_metrics)
        self.min_latency = min(latency_metrics)
        self.ninety_fifth_percentile_throughput = quantiles(
            throughput_metrics, n=20
        )[-1]
        self.ninety_fifth_percentile_latency = quantiles(
            latency_metrics, n=20
        )[-1]
        self.number_of_threads_run = len(execution_metrics)
        self.execution_info = execution_metrics


class CLILineCreator:
    """
    This class generates useful human-readable strings from all of the
    calculations, and generates a summary of the combined strings - these
    eventually get printed to stdout.
    """

    def __init__(self, metrics: Metrics):
        self._metrics = metrics

    def _execution_info_each_thread(self) -> str:
        execution_info = self._metrics.execution_info
        output_string = ""
        for item in execution_info:
            pid = item.pid
            start_time = item.start_time
            end_time = item.end_time
            start_time_human = datetime.datetime.fromtimestamp(
                start_time
            ).strftime("%c")
            end_time_human = datetime.datetime.fromtimestamp(
                end_time
            ).strftime("%c")
            total_time = round(item.total_time, 2)
            info_str = (
                f"\npid: {pid} started at {start_time_human}"
                f" and finished at {end_time_human}"
                f" taking {total_time} seconds to complete"
            )
            output_string += info_str
        return output_string

    def summary(self) -> str:
        metrics = self._metrics
        average_throughput_rounded = round(metrics.average_throughput, 2)
        average_latency_rounded = round(metrics.average_latency, 2)
        total_summary = textwrap.dedent(
            f"""\
            Average Throughput (ops/s) = {average_throughput_rounded}
            Average Latency (ms) = {average_latency_rounded}
            Max Throughput (ops/s) = {metrics.max_throughput}
            Max Latency (ms) = {metrics.max_latency}
            Min Throughput (ops/s) = {metrics.min_throughput}
            Min Latency (ms) = {metrics.min_latency}
            Throughput 95th percentile (ops/s) = {metrics.ninety_fifth_percentile_throughput}
            Latency 95th percentile (ms) = {metrics.ninety_fifth_percentile_latency}
            Total threads run = {metrics.number_of_threads_run}
            """  # noqa: E501
        )
        return total_summary + self._execution_info_each_thread()


if __name__ == "__main__":  # pragma: no cover

    """
    We use argparse to spawn N number of threads. An error is returned
    if an argument of 0 is used.
    """
    parser = argparse.ArgumentParser(
        description="Spawn stress threads for ScyllaDB and get metrics"
    )
    parser.add_argument(
        "threads",
        help="Number of threads to spawn (integer)",
        type=int,
    )

    args = parser.parse_args()

    if args.threads < 1:
        parser.error("Number of threads must be greater than 0")

    stress_tester = StressTest()
    metrics = stress_tester.run(num_threads=args.threads)
    line_creator = CLILineCreator(metrics=metrics)
    print(line_creator.summary())
