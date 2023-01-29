from multiprocessing import Process
import time, signal, os, random

events = [
    ["Strikes", 10*24],
    ["Political tensions", 30*24],
    ["Fuel shortage", 100*24],
    ["War", 300*24],
    ["Worldwide pandemic", 1000*24]
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
                        time.sleep(0.0001)
                    os.kill(os.getppid(), signal.SIGUSR1)
                    break
            time.sleep(1/24 - (time.time() - t0))
