"""
Tests for stress tester
"""

import pytest
from stress import simulate_stress
from analyze import (
    CalculateMetrics,
    CLILineCreator,
    run_processes_in_parallel,
    stress_test,
)
import time
import hashlib


class TestStressProcess:
    def test_stress_process(self) -> None:
        rows = [row for row in simulate_stress(stress_duration=3)]
        assert len(rows) == 3
        for row in rows:
            throughput = row["Throughput (ops/s)"]
            latency = row["Latency (ms)"]
            assert 0 <= throughput < 100000
            assert 0 <= latency < 20000

    @pytest.mark.parametrize("given_duration", [0, 1, 3])
    def test_duration(self, given_duration: int) -> None:
        start_time = time.monotonic()
        row = [row for row in simulate_stress(stress_duration=given_duration)]
        end_time = time.monotonic()
        time_taken = end_time - start_time
        lower_bound = given_duration
        upper_bound = given_duration + 0.1
        assert lower_bound <= time_taken <= upper_bound


class TestCalculateMetrics:
    def test_average(self) -> None:
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics = []
        expected_throughput_average = 5.5
        expected_latency_average = 5.6
        metrics = CalculateMetrics(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert metrics.average_throughput() == expected_throughput_average
        assert metrics.average_latency() == expected_latency_average

    def test_max(self) -> None:
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics = []
        expected_throughput_max = 10
        expected_latency_max = 11
        metrics = CalculateMetrics(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert metrics.max_throughput() == expected_throughput_max
        assert metrics.max_latency() == expected_latency_max

    def test_min(self) -> None:
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [0, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics = []
        expected_throughput_min = 1
        expected_latency_min = 0
        metrics = CalculateMetrics(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert metrics.min_throughput() == expected_throughput_min
        assert metrics.min_latency() == expected_latency_min

    def test_percentile_valid(self) -> None:
        throughput_metrics = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        latency_metrics = [0, 2, 3, 4, 5, 6, 7, 8, 9, 11]
        execution_metrics = []
        expected_throughput_percentile = 10.45
        expected_latency_percentile = 11.9
        metrics = CalculateMetrics(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert (
            metrics.ninety_fifth_percentile_throughput()
            == expected_throughput_percentile
        )
        assert metrics.ninety_fifth_percentile_latency() == expected_latency_percentile

    def test_percentile_invalid(self) -> None:
        throughput_metrics = [1]
        latency_metrics = [1]
        execution_metrics = []
        expected_throughput_percentile = False
        expected_latency_percentile = False
        metrics = CalculateMetrics(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert (
            metrics.ninety_fifth_percentile_throughput()
            == expected_throughput_percentile
        )
        assert metrics.ninety_fifth_percentile_latency() == expected_latency_percentile

    def test_number_processes_run(self) -> None:
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
        metrics = CalculateMetrics(
            throughput_metrics=throughput_metrics,
            latency_metrics=latency_metrics,
            execution_metrics=execution_metrics,
        )
        assert metrics.number_of_processes_run() == 1


class TestCLILineCreator:
    def test_summary(self):
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
        expected_summary_hash = "edfd1eb4326dfadcea1bf00b11b67274"
        hash_object = hashlib.md5(line_creator.summary().encode())
        hash_from_summary = hash_object.hexdigest()
        assert hash_from_summary == expected_summary_hash


class TestRunProcessesInParallel:
    @pytest.mark.parametrize("number_threads", [0, 1, 2, 3, 4, 5])
    def test_output_data_valid(self, number_threads) -> None:
        output_data = run_processes_in_parallel(
            function=stress_test,
            num_threads=number_threads,
        )

        throughput = list(output_data["throughput"])
        latency = list(output_data["latency"])
        expected_length = sum(range(1, number_threads + 1))
        actual_throughput_length = len(throughput)
        actual_latency_length = len(latency)
        assert actual_throughput_length == expected_length
        assert actual_latency_length == expected_length

        for value in throughput:
            assert 0 <= value < 100000

        for value in latency:
            assert 0 <= value < 20000
