from multiprocessing import Process
import time, signal, os, random

LOOP_DURATION = 1

events = [
    ["Strikes", 10],
    ["Political tensions", 30],
    ["Fuel shortage", 100],
    ["War", 300]
]

class External(Process):

    def __init__(self):
        super().__init__()
        self.event = False 

    def run(self):
        while True:
            t0 = time.time()
            for event in events:
                if random.randint(1, event[1]) == 1:
                    print("[External]", event[0])
                    os.kill(os.getppid(), signal.SIGUSR1)
                    for i in range(events.index(event) + 1):
                        os.kill(os.getppid(), signal.SIGUSR2)
                        time.sleep(0.01)
                    break
            time.sleep(LOOP_DURATION - (time.time() - t0))
