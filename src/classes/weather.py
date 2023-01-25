from multiprocessing import Process, Value
import time, math, random

class Weather(Process):

    def __init__(self, temperature):
        super().__init__()
        self.temperature = temperature
        self.amplitude = 4
        self.mean = 10

    def update(self, t):
        return (self.mean + self.amplitude*math.fabs(math.sin((2*math.pi*t)/48)))

    def run(self):
        for t in range(9999999):
            if t % 24 == 0 and t != 0:
                self.amplitude = random.uniform(2.0, 4.0)
                self.mean += random.randint(-2, 2)
                if self.mean < -10:
                    self.mean = -10
                elif self.mean > 35:
                    self.mean = 35
            self.temperature.value = self.update(t)
            # print("[Weather] Temperature : " + "{:.1f}".format(self.temperature.value) + "°C")
            time.sleep(0.1)
