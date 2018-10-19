import psutil
from time import *

PROCNAME = "python.exe"


def clean_python_processes(delay):
    print("Start : %s" % ctime())
    processes = [proc for proc in psutil.process_iter() if proc.name() == PROCNAME]
    for proc in processes:
        print(proc.name(), 'running ({}%)'.format(proc.cpu_percent(interval=0.2)))
        # check whether the process name matches
        if proc.cpu_percent(interval=0.2) > 20:
            cpu = proc.cpu_percent(interval=0.2)
            proc.kill()
            print(proc.name(), 'stopped ({}%)'.format(cpu))
        # break
    print("End : %s\n" % ctime())
    sleep(delay)
    clean_python_processes(delay)


# if __name__ is "__main__":
clean_python_processes(300)
