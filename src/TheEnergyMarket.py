from classes import home, market, weather, external
from multiprocessing import Value
import random, time, sysv_ipc

NUMBER_HOMES = 5

if __name__ == "__main__":
    port = random.randint(1000,2000)
    
    # Shared memory between the homes, the weather and the market
    temperature = Value('f', 10.0)
    weather = weather.Weather(temperature)
    weather.start()
    
    # Initialization of the market
    m = market.Market(port, temperature, 1.74, 2)
    m.start()
    homes = []

    # Creating the message queue
    energy_queue = sysv_ipc.MessageQueue(port, sysv_ipc.IPC_CREAT)

    # Initialization of the homes
    for i in range(int(NUMBER_HOMES)):
        homes.append(home.Home(port, i, temperature, 0, 1000, 100, 10, 3))

    # Starting all homes
    for i in range(NUMBER_HOMES):
        # print("\n", homes[i].queues)
        homes[i].start()
        # homes[i].join()
