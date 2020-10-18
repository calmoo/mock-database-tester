"""
Tests for stress tester
"""

import pytest
from stress import simulate_stress
import time


class TestStressProcess:
    def test_stress_process(self) -> None:
        rows = [row for row in simulate_stress(stress_duration=3)]
        assert len(rows) == 3
        for row in rows:
            throughput = row['Throughput (ops/s)']
            latency = row['Latency (ms)']
            assert 0 <= throughput < 100000
            assert 0 <= latency < 20000

    @pytest.mark.parametrize('given_duration', [0, 1, 3])
    def test_duration(self, given_duration: int) -> None:
        start_time = time.monotonic()
        rows = [row for row in simulate_stress(stress_duration=given_duration)]
        end_time = time.monotonic()
        time_taken = end_time - start_time
        lower_bound = given_duration
        upper_bound = given_duration + 0.1
        assert lower_bound <= time_taken <= upper_bound