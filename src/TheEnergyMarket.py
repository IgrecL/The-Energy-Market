from classes import home, market, weather, external
from multiprocessing import Value
import random, time, sysv_ipc

NUMBER_HOMES = 1

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

    # Initialization of the homes
    homes.append(home.Home(port, 1, temperature, 1000, 100, 100, 80, 3))
    # homes.append(home.Home(port, 0, 0, 100, 80, 100, 3))

    # Initialization of the queues
    for i in range(NUMBER_HOMES):
        for j in range(i):
            # print(i,j)
            i_key = port + 100 * i + j
            j_key = port + 100 * j + i
            i_q = sysv_ipc.MessageQueue(i_key, sysv_ipc.IPC_CREX)
            j_q = sysv_ipc.MessageQueue(j_key, sysv_ipc.IPC_CREX)
            homes[i].queues.append([i_q, sysv_ipc.MessageQueue(j_key)])
            homes[j].queues.append([j_q, sysv_ipc.MessageQueue(i_key)])
    
    # Starting all homes
    for i in range(NUMBER_HOMES):
        # print("\n", homes[i].queues)
        homes[i].start()
        # homes[i].join()
