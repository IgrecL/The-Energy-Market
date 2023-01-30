from classes import home, market, weather, external
from multiprocessing import Value
import random, time, sysv_ipc, matplotlib, socket, os, multiprocessing
import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
plt.style.use("dark_background")

HOST = "localhost"
PORT = 1566
NUMBER_HOMES = 3 # int
UPDATE_RATE = 2  # int
BG = "black"
FG = "white"

def digit(float, digits):
    return ("{:." + str(digits) + "f}").format(round(float, digits))

def form(int):
    return str(int) if int > 9 else "0" + str(int)

def bounds(y):
    length = len(y)
    min = y[length - 1]
    max = y[length - 1]
    for i in range(length - 100, length):
        if y[i] < min: min = y[i]
        if y[i] > max: max = y[i] 
    return [min - 0.005, max + 0.005]

def day_string(day):
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31] 
    year = 2023 + int(day / 365)
    month = 0
    while (day - month_lengths[month] > 0):
        day -= month_lengths[month]
        month = month + 1 if month < 11 else 0
    return "[" + form(day) + "/" + form(month+1) + "/" + str(year) + "]"

if __name__ == "__main__":
    # Shared memory between homes, the weather and the market
    temperature = Value('f', 10.0)
    t = Value('i', 0)
    weather = weather.Weather(temperature, t)
    weather.start()
    
    # Creating the energy and message queues
    energy_queue = sysv_ipc.MessageQueue(600, sysv_ipc.IPC_CREAT)
    print_queue = sysv_ipc.MessageQueue(700, sysv_ipc.IPC_CREAT)

    # Initialization of the market
    price = Value('f', 1.74)
    m = market.Market(temperature, price, 2)
    m.start()

    # Initialization of the homes
    homes = []
    for i in range(NUMBER_HOMES):
        energy = Value('f', 15.0)
        money = Value('f', 100.0)
        homes.append(home.Home(i, temperature, energy, money, round(random.uniform(1.0, 3.0), 2), 1.5, random.randint(1,3)))

    # Starting all homes
    for i in range(NUMBER_HOMES):
        homes[i].start()




    ### GUI 

    # Window config
    window = tk.Tk()
    window.title("The Energy Market")
    window.attributes("-fullscreen", True)
    window.configure(bg = BG)
    window.grid_columnconfigure(0, weight = 1)

    # Title
    tk.Label(window, bg = BG, fg = FG, text = "THE ENERGY MARKET", font = ("Cantarell, 40")).grid(row = 0, column = 0, pady = 20)

    # Info bar
    infobar = tk.Frame(window, bg = BG)
    infobar.grid(row = 1, column = 0, sticky = "nesw")
    infobar.grid_rowconfigure(0, weight = 100)
    infobar.grid_columnconfigure(0, weight = 50)
    infobar.grid_columnconfigure(1, weight = 50)
    time_label = tk.Label(infobar, bg = BG, fg = FG, text = "Day: 01/01/2023 01:00", font = ("Cantarell, 30"))  
    time_label.grid(row = 0, column = 0)
    temp_label = tk.Label(infobar, bg = BG, fg = FG, text = "Temperature: 30.0 °C", font = ("Cantarell, 30"))  
    temp_label.grid(row = 0, column = 1)

    # Homes grid
    homesgrid = tk.Frame(window, bg = BG)
    homesgrid.grid(row = 2, column = 0)
    house_labels = []
    policy_labels = []
    production_labels = []
    consumption_labels = []
    energy_labels = []
    money_labels = []
    for i in range(NUMBER_HOMES):
        homesgrid.grid_columnconfigure(i, weight = round(100 / NUMBER_HOMES))
        house = tk.Label(homesgrid, bg = BG, fg = "green", text = "🏠", font = ("Cantarell, 120"))
        policy = tk.Label(homesgrid, bg = BG, fg = FG, text = "Policy " + str(homes[i].policy), font = ("Cantarell, 15"))
        production = tk.Label(homesgrid, bg = BG, fg = FG, text = "+ " + str(homes[i].production) + " kWh/h", font = ("Cantarell, 15"))
        consumption = tk.Label(homesgrid, bg = BG, fg = FG, text = "- 1.0 kWh/h", font = ("Cantarell, 15"))
        energy = tk.Label(homesgrid, bg = BG, fg = FG, text = "1068.35 kWh", font = ("Cantarell, 15"))
        money = tk.Label(homesgrid, bg = BG, fg = FG, text = "30.59 €", font = ("Cantarell, 15"))
        house.grid(row = 0, column = i, padx = 10)
        policy.grid(row = 1, column = i, padx = 10)
        production.grid(row = 2, column = i, padx = 10)
        consumption.grid(row = 3, column = i, padx = 10)
        energy.grid(row = 4, column = i, padx = 10)
        money.grid(row = 5, column = i, padx = 10)
        policy_labels.append(policy)
        house_labels.append(house)
        production_labels.append(production)
        consumption_labels.append(consumption)
        energy_labels.append(energy)
        money_labels.append(money)
    
    # Bottom grid
    bottomgrid = tk.Frame(window, bg = BG)
    bottomgrid.grid(row = 3, column = 0)

    # Energy price plot
    price_fig = plt.figure(1)
    price_fig.set_figwidth(8)
    price_fig.set_figheight(4)
    plt.ion()
    x = [0]
    y = [1.74] 
    plt.plot(x, y, "r")
    plt.xlim([0, 100])
    price_canvas = FigureCanvasTkAgg(price_fig, master = bottomgrid)
    price_widget = price_canvas.get_tk_widget()
    price_widget.grid(row = 0, column = 0, sticky = "w")
    
    # Logs
    logs = tk.Text(bottomgrid, bg = BG, fg = FG, width = 65, height = 12.5, font = ("Arial", 15))
    logs.grid(row = 0, column = 1, sticky = "w")
    
    def stop():
        window.destroy()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            client_socket.send(b"3")
        time.sleep(1)
        energy_queue.remove()
        print_queue.remove()
        print("QUEUES CLOSED")
        for child in multiprocessing.active_children():
            print('Terminating', child)
            child.terminate()
            time.sleep(0.1)
        for i in range(NUMBER_HOMES):
            homes[i].join()
        print("CORRECTLY CLOSED")
        exit(0)

    # Buttons
    buttons = tk.Frame(window, bg = BG)
    buttons.grid(row = 4, column = 0)
    quit_button = tk.Button(buttons, bg = BG, fg = FG, width = 10, text = "STOP", font = ("Cantarell", 20), command = stop)
    quit_button.grid(row = 0, column = 0, pady = 30)
   
    # Updating all labels
    def update():
        A = time.time()
        
        # Updating home labels
        for i in range(NUMBER_HOMES):
            if homes[i].energy.value <= 0:
                house_labels[i].config(fg = "red")
                policy_labels[i].config(text = "-")
                production_labels[i].config(text = "-")
                consumption_labels[i].config(text = "-")
                energy_labels[i].config(text = "-")
                money_labels[i].config(text = "-")
                continue
            elif homes[i].energy.value < homes[i].energy_min:
                house_labels[i].config(fg = "orange")
            elif homes[i].energy.value > homes[i].energy_min:
                house_labels[i].config(fg = "green")
            coeff = 1 + (15 - temperature.value) / 100
            consumption_labels[i].config(text = "- " + digit(coeff * homes[i].consumption, 2) + " kWh/h")
            energy_labels[i].config(text = digit(homes[i].energy.value, 2) + " kWh")
            money_labels[i].config(text = digit(homes[i].money.value, 2) + " €")

        # Updating global labels and graph
        time_label.config(text = day_string(round(t.value / 24)) + " " + form(t.value % 24) + ":00")
        temp_label.config(text = "Temperature: " + digit(temperature.value, 1) + " °C")
        x.append(x[-1] + 1)
        y.append(price.value)
        plt.plot(x, y, "r")
        length = len(x)
        if length > 100:
            plt.xlim([length-100, length])
            plt.ylim(bounds(y))

        # Updating log
        try:
            m, type = print_queue.receive(block = False)
            logs.insert('1.0', m.decode() + "\n")
        except sysv_ipc.BusyError:
            pass

        window.after(round(UPDATE_RATE * 1000 / 24 - (time.time() - A)), update)

    update()
    window.mainloop()

