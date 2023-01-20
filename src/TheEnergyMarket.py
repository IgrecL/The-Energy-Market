from classes import home, market, weather, external
import random, time

if __name__ == "__main__":
    port = random.randint(1000,2000)
    m = market.Market(port, 2, 2)
    m.start()
    time.sleep(0.1)
    p = home.Home(port, 1, 1, 1)
    p.start()
    p2 = home.Home(port, 1, 1, 1)
    p2.start()
    p.join()
