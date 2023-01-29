from classes import home, market, weather, external
from multiprocessing import Value
import random, time, sysv_ipc, os
import numpy as np
import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
plt.style.use('dark_background')

NUMBER_HOMES = 5
BG = 'black'
FG = 'white'

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
    for i in range(NUMBER_HOMES):
        homes.append(home.Home(port, i, temperature, 15, 1000, 2.0, 1.0, 2))

    # Starting all homes
    for i in range(NUMBER_HOMES):
        # print("\n", homes[i].queues)
        homes[i].start()
        # homes[i].join()

    # Window config
    window = tk.Tk()
    window.title("The Energy Market")
    window.attributes('-fullscreen', True)
    window.configure(bg = BG)
    window.grid_columnconfigure(0, weight = 100)
    window.grid_rowconfigure(0, weight = 5)
    window.grid_rowconfigure(1, weight = 5)
    window.grid_rowconfigure(2, weight = 80)

    # Info bar
    infobar = tk.Frame(window, bg = 'blue')
    infobar.grid(row = 0, column = 0, sticky = 'nesw')
    infobar.grid_rowconfigure(0, weight = 100)
    infobar.grid_columnconfigure(0, weight = 50)
    infobar.grid_columnconfigure(1, weight = 50)
    temperature = tk.Label(infobar, bg = BG, fg = FG, text = '30.0°C', font = ("Cantarell, 30"))  
    temperature.grid(row = 0, column = 1, sticky = 'w')

    # Homes grid
    homesgrid = tk.Frame(window, bg = BG)
    homesgrid.grid(row = 1, column = 0)
    homesgrid.grid_rowconfigure(0, weight = 50)
    homesgrid.grid_rowconfigure(1, weight = 10)
    homesgrid.grid_rowconfigure(2, weight = 10)
    homesgrid.grid_rowconfigure(3, weight = 10)
    homesgrid.grid_rowconfigure(4, weight = 10)
    homesgrid.grid_rowconfigure(5, weight = 10)
    for i in range(NUMBER_HOMES):
        homesgrid.grid_columnconfigure(i, weight = round(100 / NUMBER_HOMES))
        house = tk.Label(homesgrid, bg = BG, fg = 'green', text = '🏠', font = ("Cantarell, 120"))
        energy = tk.Label(homesgrid, bg = BG, fg = FG, text = '1068.35 kWh', font = ("Cantarell, 15"))
        price = tk.Label(homesgrid, bg = BG, fg = FG, text = '30.59 €', font = ("Cantarell, 15"))
        production = tk.Label(homesgrid, bg = BG, fg = FG, text = '301.59 kWh/h', font = ("Cantarell, 15"))
        consumption = tk.Label(homesgrid, bg = BG, fg = FG, text = '301.26 kWh/h', font = ("Cantarell, 15"))
        policy = tk.Label(homesgrid, bg = BG, fg = FG, text = 'Policy 2', font = ("Cantarell, 15"))
        house.grid(row = 0, column = i, padx = 10)
        policy.grid(row = 1, column = i, padx = 10)
        production.grid(row = 2, column = i, padx = 10)
        consumption.grid(row = 3, column = i, padx = 10)
        energy.grid(row = 4, column = i, padx = 10)
        price.grid(row = 5, column = i, padx = 10)
    
    # Bottom grid
    bottomgrid = tk.Frame(window, bg = BG)
    bottomgrid.grid(row = 2, column = 0)
    bottomgrid.grid_columnconfigure(0, weight = 50)
    bottomgrid.grid_columnconfigure(1, weight = 50) 

    # Energy price plot
    price_fig = plt.figure(1)
    price_fig.set_figwidth(8)
    price_fig.set_figheight(6)
    plt.ion()
    t = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    s = [1.0, 1.1, 1.3, 1.7, 1.9, 1.7, 1.9, 1.5, 1.7, 1.5, 1.0, 1.3, 1.6, 1.5, 1.9] 
    plt.plot(t, s)
    price_canvas = FigureCanvasTkAgg(price_fig, master = bottomgrid)
    price_widget = price_canvas.get_tk_widget()
    price_widget.grid(row = 0, column = 0)
    #def update():
    #    s = np.cos(np.pi*t)
    #    plt.plot(t, s)
    #    price_fig.canvas.draw()




    termf = tk.Frame(bottomgrid, height=400, width=500)
    termf.grid(row = 0, column = 1, padx = 10)
    wid = termf.winfo_id()
    os.system('xterm -into %d -geometry 40x20 -sb &' % wid)




    window.mainloop()
