import subprocess
from multiprocessing import Process, Manager
import random
import time
import datetime
import argparse
from statistics import quantiles, mean
from typing import Callable, Dict, List, Union
import csv
import io


def stress_test(duration: int, shared_dict: dict) -> None:
    """
    This creates a process which runs ``stress.py``.
    It runs this process for ``duration`` seconds.

    It captures the standard output of this process and stores data from
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
    throughput_values_int = [int(row["Throughput (ops/s)"]) for row in rows]
    latency_values_int = [int(row["Latency (ms)"]) for row in rows]
    end_time = time.time()
    end_time_monotonic = time.monotonic()
    total_time = end_time_monotonic - start_time_monotonic
    start_time_str = datetime.datetime.fromtimestamp(start_time).strftime("%c")
    end_time_str = datetime.datetime.fromtimestamp(end_time).strftime("%c")
    process_stats = {
        "pid": stress_test_process.pid,
        "start_time": start_time_str,
        "end_time": end_time_str,
        "total_time": total_time,
    }
    shared_dict["throughput"].extend(throughput_values_int)
    shared_dict["latency"].extend(latency_values_int)
    shared_dict["execution_stats"].append(process_stats)


def run_processes_in_parallel(
    function: Callable[[int, dict], None],
    num_threads: int,
) -> Dict:
    """
    Runs the given ``function`` in ``num_threads`` threads.

    Each process is given a unique duration which is between 1 and the given
    ``num_threads``.
    """
    manager = Manager()
    shared_dict = manager.dict()  # type: ignore
    shared_dict["throughput"] = manager.list()
    shared_dict["latency"] = manager.list()
    shared_dict["execution_stats"] = manager.list()
    processes = []
    duration_list = random.sample(range(1, num_threads + 1), num_threads)
    for i in range(num_threads):
        duration = duration_list[i]
        process = Process(target=function, args=(duration, shared_dict))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    return shared_dict


class CalculateMetrics:
    """
    This class takes all of the simulated values and execution metrics
    from all of the processes run, and calculates various statistics based
    on those values.
    """
    def __init__(
        self,
        throughput_metrics: List[int],
        latency_metrics: List[int],
        execution_metrics: List[Dict],
    ):
        self.throughput_metrics = throughput_metrics
        self.latency_metrics = latency_metrics
        self.execution_metrics = execution_metrics

    def average_throughput(self) -> float:

        throughput_average = mean(self.throughput_metrics)
        return throughput_average

    def average_latency(self) -> float:
        latency_average = mean(self.latency_metrics)
        return latency_average

    def max_throughput(self) -> float:
        throughput_max = max(self.throughput_metrics)
        return throughput_max

    def max_latency(self) -> float:
        latency_max = max(self.latency_metrics)
        return latency_max

    def min_throughput(self) -> float:
        throughput_min = min(self.throughput_metrics)
        return throughput_min

    def min_latency(self) -> float:
        latency_min = min(self.latency_metrics)
        return latency_min

    def ninety_fifth_percentile_throughput(self) -> Union[float, bool]:
        if len(self.throughput_metrics) < 2:
            return False
        percentile_throughput = quantiles(self.throughput_metrics, n=20)[-1]
        return percentile_throughput

    def ninety_fifth_percentile_latency(self) -> Union[float, bool]:
        if len(self.throughput_metrics) < 2:
            return False
        percentile_latency = quantiles(self.latency_metrics, n=20)[-1]
        return percentile_latency

    def number_of_processes_run(self) -> int:
        number_processes = len(self.execution_metrics)
        return number_processes

    def execution_info(self) -> List[Dict]:
        return self.execution_metrics


class CLILineCreator:
    """
    This class generates useful human-readable strings from all of the
    calculations, and generates a summary of the combined strings - these
    eventually get printed to stdout.
    """
    def __init__(
        self,
        throughput_metrics: list,
        latency_metrics: list,
        execution_metrics: list,
    ):
        self._metrics_calculator = CalculateMetrics(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        self.execution_metrics = execution_metrics

    def _average(self) -> str:
        average_throughput = self._metrics_calculator.average_throughput()
        average_latency = self._metrics_calculator.average_latency()
        output_string = (
            f"Average Throughput = "
            f"{average_throughput} ops/s\n"
            f"Average Latency = "
            f"{average_latency}ms"
        )
        return output_string

    def _max(self) -> str:
        max_throughput = self._metrics_calculator.max_throughput()
        max_latency = self._metrics_calculator.max_latency()
        output_string = (
            f"Max throughput = "
            f"{max_throughput} ops/s\n"
            f"Max latency = {max_latency}ms"
        )
        return output_string

    def _min(self) -> str:
        min_throughput = self._metrics_calculator.min_throughput()
        min_latency = self._metrics_calculator.min_latency()
        output_string = (
            f"Min throughput = "
            f"{min_throughput} ops/s\n"
            f"Min latency = "
            f"{min_latency}ms"
        )
        return output_string

    def _percentile(self) -> str:
        percentile_throughput = (
            self._metrics_calculator.ninety_fifth_percentile_throughput()
        )
        percentile_latency = (
            self._metrics_calculator.ninety_fifth_percentile_latency()
        )
        if percentile_latency and percentile_throughput:
            output_string = (
                f"Throughput 95th percentile = "
                f"{percentile_throughput} ops/s\n"
                f"Latency 95th percentile = "
                f"{percentile_latency}ms"
            )

            return output_string

        else:
            return "Not enough data points to calculate percentile"

    def _no_processes_run(self) -> str:
        number_of_processes = (
            self._metrics_calculator.number_of_processes_run()
        )
        output_string = f"{number_of_processes} processes run in total"
        return output_string

    def _execution_info_each_process(self) -> str:
        execution_info = self._metrics_calculator.execution_info()
        output_string = ""
        for item in execution_info:
            pid = item["pid"]
            start_time = item["start_time"]
            end_time = item["end_time"]
            total_time = item["total_time"]
            info_str = (
                f"pid: {pid} started at {start_time}"
                f" and finished at {end_time}"
                f" taking  {total_time} seconds to complete\n"
            )
            output_string += info_str
        return output_string

    def summary(self) -> str:
        return (
            self._average()
            + "\n"
            + self._max()
            + "\n"
            + self._min()
            + "\n"
            + self._percentile()
            + "\n"
            + self._no_processes_run()
            + "\n"
            + self._execution_info_each_process()
        )


if __name__ == "__main__":

    """
    We use argparse to spawn N number of processes. An error is returned
    if an argument of 0 is used.
    """
    parser = argparse.ArgumentParser(
        description="Spawn stress processes for ScyllaDB and get metrics"
    )
    parser.add_argument(
        "threads",
        help="Number of processes to spawn (integer)",
        type=int,
    )

    args = parser.parse_args()

    if args.threads < 1:
        parser.error("Number of threads must be greater than 0")

    output_data = run_processes_in_parallel(
        function=stress_test,
        num_threads=args.threads,
    )

    throughput = list(output_data["throughput"])
    latency = list(output_data["latency"])
    execution_metrics = list(output_data["execution_stats"])

    line_creator = CLILineCreator(
        throughput_metrics=throughput,
        latency_metrics=latency,
        execution_metrics=execution_metrics,
    )

    print(line_creator.summary())
