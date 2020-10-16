import subprocess
from multiprocessing import Process, Array
import random


def stress_test(duration: int, shared_metrics: dict) -> str:
    stress_test = subprocess.Popen(["python","stress.py",
                                    str(duration)],
                                   stdout=subprocess.PIPE)
    stress_test_output = stress_test.communicate()[0].decode('utf-8')
    throughput_values = stress_test_output[0::2]
    latency_values = stress_test_output[1::2]
    shared_metrics["throughput"].extend(throughput_values)
    shared_metrics["latency"].extend(latency_values)
    return stress_test_output

def run_processes_in_parallel(function, num_threads, shared_metrics):
    processes = []
    for i in range(num_threads):
        duration = random.randrange(1,7)
        process = Process(target=function, args=(duration, shared_metrics))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    print(shared_metrics)




if __name__ == '__main__':
    arr_throughput = []
    arr_latency = []
    shared_metrics = {"throughput": [], "latency": []}
    run_processes_in_parallel(stress_test, 8, shared_metrics)
