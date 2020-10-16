import subprocess
from multiprocessing import Process, Array
import random
arr2 = []


def stress_test(duration: int, arr) -> str:
    stress_test = subprocess.Popen(["python","stress.py",
                                    str(duration)],
                                   stdout=subprocess.PIPE)
    stress_test_output = stress_test.communicate()[0].decode('utf-8')
    throughput_values = stress_test_output[0::2]
    latency_values = stress_test_output[1::2]

    return stress_test_output

def run_processes_in_parallel(function, num_threads):
    processes = []
    for i in range(num_threads):
        duration = random.randrange(1,7)
        process = Process(target=function, args=(duration, arr))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()


if __name__ == '__main__':

    run_processes_in_parallel(stress_test, 8)

