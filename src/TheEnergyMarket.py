from classes import home, market, weather, external
from multiprocessing import Value
import random, time, sysv_ipc

NUMBER_HOMES = 2

if __name__ == "__main__":
    port = random.randint(1000,2000)
    
    # Shared memory between the homes, the weather and the market
    temperature = Value('f', 10.0)
    weather = weather.Weather(temperature)
    weather.start()

    # Initialization of the market
    m = market.Market(port, temperature, 1.74, 2)
    m.start()
    time.sleep(0.1)
    homes = []

    # Creating the message queue
    energy_queue = sysv_ipc.MessageQueue(port, sysv_ipc.IPC_CREAT)

    # Initialization of the homes
    homes.append(home.Home(port, 1, temperature, 0, 100, 100, 80, 2))
    homes.append(home.Home(port, 2, temperature, 0, 100, 90, 100, 1))
    #homes.append(home.Home(port, 3, temperature, 0, 100, 80, 100, 1))
    
    # Starting all homes
    for i in range(NUMBER_HOMES):
        # print("\n", homes[i].queues)
        homes[i].start()
        # homes[i].join()
