"""
Tests for stress tester
"""

import pytest
from stress import simulate_stress
from analyze import (
    MetricsCalculator,
    CLILineCreator,
    run_threads_in_parallel,
    stress_test,
)
import time
from typing import List, Dict


class TestStressProcess:
    def test_stress_process(self) -> None:
        """
        The stress simulator should return two values (one row) per second of
        duration. These values should be within the constraints of:
        Throughput < 100000
        Latency < 20000
        """
        rows = [row for row in simulate_stress(stress_duration=3)]
        assert len(rows) == 3
        for row in rows:
            throughput = row["Throughput (ops/s)"]
            latency = row["Latency (ms)"]
            assert 0 <= throughput < 100000
            assert 0 <= latency < 20000

    @pytest.mark.parametrize("given_duration", [0, 1, 3])
    def test_duration(self, given_duration: int) -> None:
        """
        The stress simulator should finish executing within reasonable time
        of the duration specified, here are a tolerance of +0.3s is set.
        """
        start_time = time.monotonic()
        _ = [row for row in simulate_stress(stress_duration=given_duration)]
        end_time = time.monotonic()
        time_taken = end_time - start_time
        lower_bound = given_duration
        upper_bound = given_duration + 0.3
        assert lower_bound <= time_taken <= upper_bound


class TestCalculateMetrics:
    def test_average(self) -> None:
        """
        Average of values can be calculated accurately.
        """
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics: List = []
        expected_throughput_average = 5.5
        expected_latency_average = 5.6
        metrics = MetricsCalculator(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert metrics.average_throughput() == expected_throughput_average
        assert metrics.average_latency() == expected_latency_average

    def test_max(self) -> None:
        """
        Maximum of values can be calculated accurately.
        """
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics: List = []
        expected_throughput_max = 10
        expected_latency_max = 11
        metrics = MetricsCalculator(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert metrics.max_throughput() == expected_throughput_max
        assert metrics.max_latency() == expected_latency_max

    def test_min(self) -> None:
        """
        Minimum of values can be calculated accurately.
        """
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [0, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics: List = []
        expected_throughput_min = 1
        expected_latency_min = 0
        metrics = MetricsCalculator(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert metrics.min_throughput() == expected_throughput_min
        assert metrics.min_latency() == expected_latency_min

    def test_percentile_valid(self) -> None:
        """
        95th percentile of values can be calculated accurately.
        """
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [0, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics: List = []
        expected_throughput_percentile = 10.45
        expected_latency_percentile = 11.9
        metrics = MetricsCalculator(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert (
            metrics.ninety_fifth_percentile_throughput()
            == expected_throughput_percentile
        )
        assert metrics.ninety_fifth_percentile_latency() == (
            expected_latency_percentile
        )

    def test_number_threads_run(self) -> None:
        """
        The number of execution info items should be counted accurately.
        """
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [0, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics = [
            {
                "pid": 80819,
                "start_time": "Sun Oct 18 17:43:41 2020",
                "end_time": "Sun Oct 18 17:43:42 2020",
                "total_time": 1.065514607,
            }
        ]
        metrics = MetricsCalculator(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert metrics.number_of_threads_run() == 1


class TestCLILineCreator:
    def test_summary(self) -> None:
        """
        The summary of all threads should be printed accurately.
        For cleanliness and avoiding formatting headaches, a manually verified
        print output is read from ``expected_summary.txt`` and compared to
        the output value from the code.
        """
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [0, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics = [
            {
                "pid": 80819,
                "start_time": "Sun Oct 18 17:43:41 2020",
                "end_time": "Sun Oct 18 17:43:42 2020",
                "total_time": 1.065514607,
            }
        ]
        line_creator = CLILineCreator(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )

        from pathlib import Path

        expected_contents_file = Path(__file__).parent / "expected_summary.txt"
        expected_contents = expected_contents_file.read_text()
        assert expected_contents == line_creator.summary()


class TestRunThreadsInParallel:
    @pytest.mark.parametrize("number_threads", [0, 1, 2, 3, 4, 5])
    def test_output_data_valid(self, number_threads: int) -> None:
        """
        The number of simulated values and range of values should be accurate
        when run in parallel.
        """
        output_data = run_threads_in_parallel(
            function=stress_test,
            num_threads=number_threads,
        )

        throughput = list(output_data["throughput"])
        latency = list(output_data["latency"])
        expected_length = sum(range(2, number_threads + 2))
        actual_throughput_length = len(throughput)
        actual_latency_length = len(latency)
        assert actual_throughput_length == expected_length
        assert actual_latency_length == expected_length

        for value in throughput:
            assert 0 <= value < 100000

        for value in latency:
            assert 0 <= value < 20000

    @pytest.mark.parametrize("number_threads", [1, 2, 3, 4, 5])
    def test_timing(self, number_threads: int) -> None:
        """
        The maximum time of a thread should be accurate when run in parallel.
        Here a tolerance of 0.5 is set, as the timing error increases for
        a larger number of threads. 1 is added to the tolerance, as the minimum
        execution time is always at least 2 seconds.
        """
        output_data = run_threads_in_parallel(
            function=stress_test,
            num_threads=number_threads,
        )
        execution_metrics = list(output_data["execution_stats"])
        times = []
        for item in execution_metrics:
            total_time = item["total_time"]
            times.append(total_time)
        actual_longest_time = max(times)
        lower_bound = number_threads
        upper_bound = number_threads + 1.5
        assert lower_bound < actual_longest_time < upper_bound


class TestStressTestCaller:
    """
    The stress_test caller function should mutate the lists in the dictionary
    correctly.
    """

    def test_dict_results(self) -> None:
        dict_input: Dict = {
            "throughput": [], "latency": [], "execution_stats": []
        }
        stress_test(duration=1, shared_dict=dict_input)
        for key in dict_input:
            assert len(dict_input[key]) == 1
