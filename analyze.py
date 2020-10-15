import subprocess
from multiprocessing import Process, Array
import random


def stress_test(duration: int, throughput: list, latency: list) -> str:
    stress_test = subprocess.Popen(["python","stress.py",
                                    str(duration)],
                                   stdout=subprocess.PIPE)
    stress_test_output = stress_test.communicate()[0].decode('utf-8')
    throughput_values = raw_stdout[0::2]
    latency_values = raw_stdout[1::2]
    throughput.extend(throughput_values)
    latency.extend(latency_values)
    return stress_test_output

def run_processes_in_parallel(function, num_threads):
    processes = []
    for i in range(num_threads):
        duration = random.randrange(1,7)
        process = Process(target=function, args=(duration,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()


raw_stdout = stress_test(5).split()[4:]
print(raw_stdout)

print(raw_stdout[1::2])
print(raw_stdout[0::2])

if __name__ == '__main__':
    arr_throughput = []
    arr_latency = []
    run_processes_in_parallel(stress_test, 8)