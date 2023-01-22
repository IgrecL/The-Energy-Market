from classes import home, market, weather, external
import random, time, sysv_ipc

NUMBER_HOMES = 2

if __name__ == "__main__":
    port = random.randint(1000,2000)
    m = market.Market(port, 2, 2)
    m.start()
    time.sleep(0.1)
    homes = []
    
    # Initialization of the homes
    homes.append(home.Home(port, 1000, 100, 80, 1))
    homes.append(home.Home(port, 0, 80, 100, 1))
    
    # Initialization of the queues
    for i in range(NUMBER_HOMES):
        for j in range(i):
            print(i,j)
            i_key = port + 100 * i + j
            j_key = port + 100 * j + i
            i_q = sysv_ipc.MessageQueue(i_key, sysv_ipc.IPC_CREX)
            j_q = sysv_ipc.MessageQueue(j_key, sysv_ipc.IPC_CREX)
            homes[i].queues.append([i_q, sysv_ipc.MessageQueue(j_key)])
            homes[j].queues.append([j_q, sysv_ipc.MessageQueue(i_key)])
    
    # Starting all homes
    for i in range(NUMBER_HOMES):
        print("\n", homes[i].queues)
        homes[i].start()
        # homes[i].join()
