# ScyllaDB Stress simulation
This is a mock database tester and CLI program that runs a thread which generates random latency and throughput
values for a set duration of seconds, while also running these threads in parallel. A summary of these threads is
printed after execution has completed.

Tested on Python 3.8.

## Usage
The number of threads to spawn is passed as an integer when running the program. This value must be larger than 0.

Spawn 3 stress threads in parallel and analyze the results:

```
python analyze.py 3
```

Sample output:

```
Average Throughput (ops/s) = 43837.33
Average Latency (ms) = 11324.67
Max Throughput (ops/s) = 91320
Max Latency (ms) = 17923
Min Throughput (ops/s) = 1903
Min Latency (ms) = 2431
Throughput 95th percentile (ops/s) = 94027.5
Latency 95th percentile (ms) = 17973.0
Total threads run = 3

pid: 47789 started at Wed Oct 21 12:17:14 2020 and finished at Wed Oct 21 12:17:16 2020 taking 2.12 seconds to complete
pid: 47790 started at Wed Oct 21 12:17:14 2020 and finished at Wed Oct 21 12:17:17 2020 taking 3.13 seconds to complete
pid: 47791 started at Wed Oct 21 12:17:14 2020 and finished at Wed Oct 21 12:17:18 2020 taking 4.13 seconds to complete

```
The stress.py program can also be run independently with no analysis,
the duration of the thread is passed as an argument:

```
python stress.py 3
```

Output:
```
Throughput (ops/s),Latency (ms)
78433,10286
28372,19763
16316,6240
```

## How to run the tests:

Install test requirements:

```
pip install -r dev-requirements.txt
```

Run tests:

```
pytest
```

## Decisions made:

- I included list comprehension and a generator in the code as I wanted to become more familiar with them after 
our initial interview.

- Apart from pytest, all imports are standard libraries for improved maintainability and less overhead.

- Initially the program wrote to stdout in columns seperated by spaces - this was later changed to a CSV style
output to simplify output parsing and to reduce any future parsing errors.

- The summary values are rounded to two decimal places for readability.

- The tests are comprehensive and have thorough coverage. The code is fully typed with mypy and linted with flake8:

```
pytest --cov-fail-under 100 --cov tests/ --cov analyze --cov stress
flake8 .
mypy tests stress.py analyze.py
```