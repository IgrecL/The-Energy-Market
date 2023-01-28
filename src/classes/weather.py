from multiprocessing import Process, Value
import time, math, random

def form(int):
    return str(int) if int > 9 else "0" + str(int)

def day_string(day):
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] 
    year = 2023 + int(day / 365)
    month = 0
    while (day - month_lengths[month] > 0):
        day -= month_lengths[month]
        month = month + 1 if month < 11 else 0
    return "[" + form(day) + "/" + form(month+1) + "/" + str(year) + "]"

class Weather(Process):

    def __init__(self, temperature):
        super().__init__()
        self.temperature = temperature

    def run(self):
        day = 0
        mean = 0.0
        amplitude = 0.0
        while True:
            t0 = time.time()
            if (day % 365 == 0):
                mean = 20.0 + random.uniform(-3.0, 3.0)
                amplitude = 20.0 + random.uniform(-5.0, 5.0)
                print("[Weather] For this year: Mean " + "{:.1f}".format(mean) + "°C | Amplitude " + "{:.1f}".format(amplitude) + "°C")

            # The mean temperature of the day is calculated with a cosinus centered on 'mean' + some randomness
            self.temperature.value = mean + amplitude * math.cos(math.pi + 2 * math.pi * day / 365.0) + random.uniform(-1.0, 1.0)
            if day != 0:
                print("[Weather] Temperature :", "{:.1f}".format(self.temperature.value), "°C", day_string(day))
            
            time.sleep(1 - (time.time() - t0))
            day += 1
