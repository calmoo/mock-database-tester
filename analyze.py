import subprocess
from multiprocessing import Process, Array, Pool, Manager
import random
arr2 = []
import time
import datetime
import pprint

def stress_test(duration: int, d: dict) -> None:
    """
    Modifications to mutable values or items in dict and list proxies will not
    be propagated through the manager, because the proxy has no way of knowing
    when its values or items are modified. To modify such an item,
    you can re-assign the modified object to the container proxy.
    https://docs.python.org/2/library/multiprocessing.html#multiprocessing.managers.SyncManager.list
    """
    start_time = time.time()
    stress_test = subprocess.Popen(["python","stress.py",
                                    str(duration)],
                                   stdout=subprocess.PIPE)
    stress_test_output = stress_test.communicate()[0].decode('utf-8').split()[4:]
    end_time = time.time()
    total_time = end_time - start_time
    start_time = datetime.datetime.fromtimestamp(start_time).strftime('%c')
    end_time = datetime.datetime.fromtimestamp(end_time).strftime('%c')
    throughput_values = stress_test_output[0::2]
    latency_values = stress_test_output[1::2]
    d["throughput"].extend(throughput_values)
    d["latency"].extend(latency_values)
    pid = stress_test.pid
    d['execution_stats'].append("pid: {} started at {} and finished at {}"
                                " and took {} seconds"
                                .format(pid,start_time,end_time, total_time)
                                )
    print(stress_test.pid)

if __name__ == '__main__':
    def run_processes_in_parallel(function, num_threads):
        manager = Manager()
        shared_dict = manager.dict()
        shared_dict["throughput"] = manager.list()
        shared_dict["latency"] = manager.list()
        shared_dict["execution_stats"] = manager.list()
        processes = []
        for i in range(num_threads):
            duration = random.randrange(1, 7)
            process = Process(target=function, args=(duration, shared_dict))
            process.start()
            processes.append(process)
        for process in processes:
            process.join()

        print(shared_dict["throughput"][:])
        print(shared_dict["latency"][:])
        pprint.pprint((shared_dict["execution_stats"][:]))
    run_processes_in_parallel(stress_test, 5)
   # stress_test(4,{})
