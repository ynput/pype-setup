import threading
import time


def loop_for_ever():
    while True:
        string = "looping for ever."
        print(string)
        if len(string) <= len("looping for ever......................................."):
            string += "."


def doit(arg):
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        print("working on %s" % arg)
        loop_for_ever()
    print("Stopping as you wish.")


def main():
    t = threading.Thread(target=doit, args=("task",))
    t.start()
    time.sleep(5)
    t.do_run = False
    t.join()


if __name__ == "__main__":
    main()
