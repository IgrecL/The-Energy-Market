from multiprocessing import Process, Value
import time, math, random

class Weather(Process):

    def __init__(self, speed, temperature, t):
        super().__init__()
        self.speed = speed
        self.temperature = temperature
        self.t = t

    def run(self):
        day = 0
        year_mean = 20.0
        year_amplitude = 20.0
        day_mean = 15.0
        day_amplitude = 3.0
        while True:
            t0 = time.time()
            t = self.t.value

            # Once a day
            if t % 24 == 0:
                day = int(t / 24)

                # Once a year
                if (day % 365 == 0):
                    year_mean = 15.0 + random.uniform(-3.0, 3.0)
                    year_amplitude = 20.0 + random.uniform(-5.0, 5.0)
                    print("[Weather] For this year: Mean " + str(round(year_mean, 1)) + "°C | Amplitude " + str(round(year_amplitude, 1)) + "°C")

                # The mean temperature of the day is calculated with a cosinus centered on 'mean' + some randomness
                day_mean = year_mean + year_amplitude * math.cos(math.pi + 2 * math.pi * day / 365.0) + random.uniform(-1.0, 1.0)
                day_amplitude = random.uniform(2.0, 5.0)
            
            self.temperature.value = day_mean + day_amplitude * math.fabs(math.sin((2 * math.pi * t) / 48))
            if 1 / (24 * self.speed.value) - (time.time() - t0) > 0:
                time.sleep(1 / (24 * self.speed.value) - (time.time() - t0))
            self.t.value += 1

