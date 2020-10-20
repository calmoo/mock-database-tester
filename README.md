# ScyllaDB Stress simulation
This is a mock database tester and CLI program that runs a process which generates random latency and throughput
values for a set duration of seconds, while also running these processes in parallel. A summary of these processes is
printed after execution has completed.

## Usage
The number of processes to spawn is passed as an integer when running the program. This value must be larger than 0.

Spawn 3 stress processes in parallel and analyze the results:

```
python analyze.py 3
```

Sample output:
```
Average Throughput = 38587.89 ops/s
Average Latency = 9331.78ms
Max throughput = 87622 ops/s
Max latency = 17266ms
Min throughput = 747 ops/s
Min latency = 304ms
Throughput 95th percentile = 90609.5 ops/s
Latency 95th percentile = 18183.0ms
3 processes run in total
pid: 26849 started at Tue Oct 20 17:57:52 2020 and finished at Tue Oct 20 17:57:54 2020 taking  2.09 seconds to complete
pid: 26847 started at Tue Oct 20 17:57:52 2020 and finished at Tue Oct 20 17:57:55 2020 taking  3.09 seconds to complete
pid: 26848 started at Tue Oct 20 17:57:52 2020 and finished at Tue Oct 20 17:57:56 2020 taking  4.09 seconds to complete
```
The stress.py process can also be run independently with no analysis,
the duration of the process is passed as an argument:

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
Tested on Python 3.8. The tests 
```
pip install -r dev-requirements.txt
pytest
```

## Decisions made:

- For multithreading, I used the multiprocessing libray. The Process class was used over the Pool class , as the Pool
 class waits for a process to complete
an operation before scheduling another one. As this program is IO bound (reads stdout which is delayed every second),
the Process class was used, as it halts the current process and scheduled another one.

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