from multiprocessing import Process
import time, signal, os, random

events = [
    ["Strikes", 20],
    ["Political tensions", 50],
    ["Fuel shortage", 200],
    ["War", 500]
]

class External(Process):

    def __init__(self):
        super().__init__()
        self.event = False 

    def run(self):
        while True:
            for event in events:
                if random.randint(1, event[1]) == 1:
                    print("[External]", event[0])
                    os.kill(os.getppid(), signal.SIGUSR1)
                    for i in range(events.index(event) + 1):
                        os.kill(os.getppid(), signal.SIGUSR2)
                        time.sleep(0.01)
                    break
            time.sleep(1)
