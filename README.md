# ScyllaDB Stress simulation
This is a mock database tester and CLI program that runs a process which generates random latency and throughput
values for a set duration of seconds, while also running these processes in parallel.

## Usage
Spawn 3 stress processes in parallel and analyze the results:

```python analyze.py 3```

Sample output:
```
Average Throughput = 44036.5 ops/s
Average Latency = 9102.333333333334ms
Max throughput = 80085 ops/s
Max latency = 18705ms
Min throughput = 8779 ops/s
Min latency = 2881ms
Throughput 95th percentile = 80105.15 ops/s
Latency 95th percentile = 23951.8ms
3 processes run in total
pid: 91365 started at Sun Oct 18 19:49:00 2020 and finished at Sun Oct 18 19:49:01 2020 taking  1.0824404859999999 seconds to complete
pid: 91367 started at Sun Oct 18 19:49:00 2020 and finished at Sun Oct 18 19:49:02 2020 taking  2.085682722 seconds to complete
pid: 91366 started at Sun Oct 18 19:49:00 2020 and finished at Sun Oct 18 19:49:03 2020 taking  3.086642045 seconds to complete

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
Tested on Python 3.8
```
pip install -r dev-requirements.txt
pytest
```