import subprocess


def run_stress_test(duration: int) -> str:
    stress_test = subprocess.Popen(["python","stress.py",
                                    str(duration)],
                                   stdout=subprocess.PIPE)
    stress_test_output = stress_test.communicate()[0].decode('utf-8')
    return stress_test_output


run_stress_test(2)

