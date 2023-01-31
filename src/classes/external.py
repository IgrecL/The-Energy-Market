from multiprocessing import Process
import time, signal, os, random, sysv_ipc

events = [
    ["Strikes", 20*24],
    ["Political tensions", 50*24],
    ["Fuel shortage", 200*24],
    ["War", 500*24],
    ["Worldwide pandemic", 2000*24]
]

class External(Process):

    def __init__(self, speed):
        super().__init__()
        self.print = sysv_ipc.MessageQueue(700)
        self.speed = speed

    def run(self):
        while True:
            t0 = time.time()
            for event in events:
                if random.randint(1, event[1]) == 1:
                    self.print.send(("[External] " + event[0]).encode())
                    os.kill(os.getppid(), signal.SIGUSR1)
                    for i in range(events.index(event) + 1):
                        os.kill(os.getppid(), signal.SIGUSR2)
                        time.sleep(0.0001)
                    os.kill(os.getppid(), signal.SIGUSR1)
                    break
            if 1 / (24 * self.speed.value) - (time.time() - t0) > 0:
                time.sleep(1 / (24 * self.speed.value) - (time.time() - t0))
