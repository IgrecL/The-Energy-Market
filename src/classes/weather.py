from multiprocessing import Process
 
class Weather(Process):

    def __init__(self, initial_temperature):
        super().__init__()
        self.temperature = initial_temperature
        self.temp_variation = 0.5
        self.raining = False

    def run(self):
        print("Weather")
