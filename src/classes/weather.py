from multiprocessing import Process, Value
import time, math, random

def digit(float):
    return "{:.1f}".format(round(float, 1))

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
        t = 0
        day = 0
        year_mean = 20.0
        year_amplitude = 20.0
        day_mean = 15.0
        day_amplitude = 3.0
        while True:
            t0 = time.time()

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
            
            # Midday
            if (t + 12) % 24 == 0:
                print("[Weather] Temperature: " + digit(self.temperature.value) + "°C", day_string(day), "[" + str(t % 24) + ":00]")

            self.temperature.value = day_mean + day_amplitude * math.fabs(math.sin((2 * math.pi * t) / 48))
            time.sleep(1/24 - (time.time() - t0))
            t += 1

