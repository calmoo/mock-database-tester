import subprocess
from multiprocessing import Process, Manager
import random
import time
import datetime
import pprint
import argparse
import statistics
from typing import Callable, Dict, List

# parser = argparse.ArgumentParser(
#     description="Spawn multiple stress processes for ScyllaDB and get metrics"
# )
# parser.add_argument(
#     "number_of_processes", help="Number of processes to spawn", type=int
# )
# parser.add_argument(
#     "max_duration_of_processes", help="Max duration of processes", type=int
# )
# args = parser.parse_args()


def stress_test(duration: int, shared_dict: dict) -> None:

    start_time = time.time()
    stress_test = subprocess.Popen(
        ["python", "stress.py", str(duration)], stdout=subprocess.PIPE
    )
    stress_test_output = stress_test.communicate()[0].decode("utf-8").split()[4:]
    end_time = time.time()
    total_time = end_time - start_time

    start_time_str = datetime.datetime.fromtimestamp(start_time).strftime("%c")
    end_time_str = datetime.datetime.fromtimestamp(end_time).strftime("%c")
    throughput_values = stress_test_output[0::2]
    latency_values = stress_test_output[1::2]
    throughput_values_int = [int(i) for i in throughput_values]
    latency_values_values_int = [int(i) for i in latency_values]
    shared_dict["throughput"].extend(throughput_values_int)
    shared_dict["latency"].extend(latency_values_values_int)
    pid = stress_test.pid
    shared_dict["execution_stats"].append(
        "pid: {} started at {} and finished at {}"
        " and took {} seconds".format(pid, start_time_str, end_time_str, total_time)
    )
    print(stress_test.pid)


def run_processes_in_parallel(function: Callable[[int, dict], None], num_threads: int, max_duration: int) -> Dict:
    manager = Manager()
    shared_dict = manager.dict() # type: ignore
    shared_dict["throughput"] = manager.list()
    shared_dict["latency"] = manager.list()
    shared_dict["execution_stats"] = manager.list()
    processes = []
    duration_list = random.sample(range(0, max_duration), num_threads)
    for i in range(num_threads):
        duration = duration_list[i]
        process = Process(target=function, args=(duration, shared_dict))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()

    return dict(shared_dict)


class CalculateMetrics:
    def __init__(
        self, throughput_metrics: List[int], latency_metrics: List[int]):
        self.throughput_metrics = throughput_metrics
        self.latency_metrics = latency_metrics

    def average_throughput(self) -> float:

        throughput_average = sum(self.throughput_metrics) / len(self.throughput_metrics)
        return throughput_average

    def average_latency(self) -> float:
        latency_average = sum(self.latency_metrics) / len(self.latency_metrics)
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

    def ninety_fifth_percentile_throughput(self) -> float:
        percentile_throughput = (
            statistics.quantiles(self.throughput_metrics, n=20)[-1]
        )
        return percentile_throughput

    def ninety_fifth_percentile_latency(self) -> float:
        percentile_latency = (
            statistics.quantiles(self.latency_metrics, n=20)[-1]
        )
        return percentile_latency

class CLILineCreator:

    def __init__(self, throughput_metrics: list, latency_metrics: list):
        self._metrics_calculator = CalculateMetrics(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
        )
        #self._execution_stats = execution_stats

    def average(self) -> str:
        average_throughput = self._metrics_calculator.average_throughput()
        average_latency = self._metrics_calculator.average_latency()
        output_string = (
            f"Average Throughput = {average_throughput} ops/s\n"
            f"Average Latency = {average_latency}ms"
        )
        return output_string

    def max(self) -> str:
        max_throughput = self._metrics_calculator.max_throughput()
        max_latency = self._metrics_calculator.max_latency()
        output_string = (
            f"Max throughput = {max_throughput} ops/s\n"
            f"Max latency = {max_latency}ms"
        )
        return output_string

    def min(self) -> str:
        min_throughput = self._metrics_calculator.min_throughput()
        min_latency = self._metrics_calculator.min_latency()
        output_string = (
            f"Min throughput = {min_throughput} ops/s\n"
            f"Min latency = {min_latency}ms"
        )
        return output_string

    def percentile(self) -> str:
        percentile_throughput = self._metrics_calculator.ninety_fifth_percentile_throughput()
        percentile_latency = self._metrics_calculator.ninety_fifth_percentile_latency()
        output_string = (
            f"Throughput 95th percentile = {percentile_throughput} ops/s\n"
            f"Latency 95th percentile = {percentile_latency}ms"
            )

        return output_string

if __name__ == "__main__":
    # output_data = run_processes_in_parallel(
    #     function=stress_test,
    #     max_duration=args.max_duration_of_processes,
    #     num_threads=args.number_of_processes,
    # )
    #
    output_data = run_processes_in_parallel(
        function=stress_test,
        max_duration=6,
        num_threads=3,
    )
    throughput = output_data["throughput"][:]
    latency = output_data["latency"][:]
    execution_stats = output_data["execution_stats"][:]

    calculator = CLILineCreator(throughput_metrics=throughput,latency_metrics=latency)

    print(calculator.average())
    print(calculator.max())
    print(calculator.min())
    print(calculator.percentile())
