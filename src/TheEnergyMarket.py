from classes import home, market, weather, external
from multiprocessing import Value
import random, time, sysv_ipc, matplotlib, socket,multiprocessing, sys
import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
plt.style.use("dark_background")

HOST = "localhost"
PORT = 1566
UPDATE_RATE = 1  # int
NUMBER_HOMES = 3 # int
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
    global speed
    speed = Value('f', 0.5)
    temperature = Value('f', 10.0)
    t = Value('i', 0)
    weather = weather.Weather(speed, temperature, t)
    weather.start()
    
    # Creating the energy and message queues
    energy_queue = sysv_ipc.MessageQueue(600, sysv_ipc.IPC_CREAT)
    print_queue = sysv_ipc.MessageQueue(700, sysv_ipc.IPC_CREAT)

    # Initialization of the market
    price = Value('f', 1.74)
    m = market.Market(speed, temperature, price, 2)
    m.start()

    # Preset selection
    preset = sys.argv[1]
    homes = []
    if preset == "1":
        energy = Value('f', 30.0)
        money = Value('f', 100.0)
        homes.append(home.Home(speed, 0, temperature, energy, money, 1.5, 2, 2))
        energy = Value('f', 20.0)
        money = Value('f', 500.0)
        homes.append(home.Home(speed, 1, temperature, energy, money, 2.0, 4, 3))
    elif preset == "2":
        energy = Value('f', 30.0)
        money = Value('f', 100.0)
        homes.append(home.Home(speed, 0, temperature, energy, money, 3.0, 1, 1))
        energy = Value('f', 20.0)
        money = Value('f', 100.0)
        homes.append(home.Home(speed, 1, temperature, energy, money, 1.2, 3, 3))
        energy = Value('f', 20.0)
        money = Value('f', 100.0)
        homes.append(home.Home(speed, 2, temperature, energy, money, 0.8, 2, 3))
    elif preset == "3":
        print("")
    else:
        for i in range(NUMBER_HOMES):
            energy = Value('f', 15.0)
            money = Value('f', 500.0)
            randint = random.randint(1, 4)
            homes.append(home.Home(speed, i, temperature, energy, money, randint * random.uniform(0.5, 0.6), randint, random.randint(1, 3)))

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
    time_label = tk.Label(infobar, bg = BG, fg = FG, text = "Day: 01/01/2023 01:00", font = ("Cantarell, 25"))  
    time_label.grid(row = 0, column = 0)
    temp_label = tk.Label(infobar, bg = BG, fg = FG, text = "Temperature: 30.0 °C", font = ("Cantarell, 25"))  
    temp_label.grid(row = 0, column = 1)

    # Homes grid
    homesgrid = tk.Frame(window, bg = BG)
    homesgrid.grid(row = 2, column = 0)
    house_labels = []
    person_labels = []
    name_labels = []
    policy_labels = []
    production_labels = []
    consumption_labels = []
    energy_labels = []
    money_labels = []
    for i in range(NUMBER_HOMES):
        homesgrid.grid_columnconfigure(i, weight = round(100 / NUMBER_HOMES))
        person_string = ""
        for j in range(int(homes[i].consumption / 0.5)):
            person_string += "☻" 
        house = tk.Label(homesgrid, bg = BG, fg = "green", text = "🏠", font = ("Cantarell, 110"))
        person = tk.Label(homesgrid, bg = BG, fg = "green", text = person_string, font = ("Cantarell, 15"))
        name = tk.Label(homesgrid, bg = BG, fg = FG, text = "Home " + str(i), font = ("Cantarell, 15"))
        policy = tk.Label(homesgrid, bg = BG, fg = FG, text = "Policy " + str(homes[i].policy), font = ("Cantarell, 15"))
        production = tk.Label(homesgrid, bg = BG, fg = FG, text = "+ " + str(homes[i].production) + " kWh/h", font = ("Cantarell, 15"))
        consumption = tk.Label(homesgrid, bg = BG, fg = FG, text = "- 1.0 kWh/h", font = ("Cantarell, 15"))
        energy = tk.Label(homesgrid, bg = BG, fg = FG, text = "1068.35 kWh", font = ("Cantarell, 15"))
        money = tk.Label(homesgrid, bg = BG, fg = FG, text = "30.59 €", font = ("Cantarell, 15"))
        house.grid(row = 0, column = i, padx = 10)
        person.grid(row = 1, column = i, padx = 10)
        name.grid(row = 2, column = i, padx = 10)
        policy.grid(row = 3, column = i, padx = 10)
        production.grid(row = 4, column = i, padx = 10)
        consumption.grid(row = 5, column = i, padx = 10)
        energy.grid(row = 6, column = i, padx = 10)
        money.grid(row = 7, column = i, padx = 10)
        house_labels.append(house)
        person_labels.append(person)
        name_labels.append(name)
        policy_labels.append(policy)
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
    
    def change_speed():
        if speed.value == 0.50:
            speed.value = 1.00 
            speed_button.config(text = "SPEED x1.00")
        elif speed.value == 1.00:
            speed.value = 0.25 
            speed_button.config(text = "SPEED x0.25")
        elif speed.value == 0.25:
            speed.value = 0.50
            speed_button.config(text = "SPEED x0.50")

    def stop():
        window.destroy()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            client_socket.send(b"3")
        time.sleep(2)
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
    speed_button = tk.Button(buttons, bg = BG, fg = FG, width = 10, text = "SPEED x0.50", font = ("Cantarell", 20), command = change_speed)
    speed_button.grid(row = 0, column = 0, padx = 10, pady = 10)
    quit_button = tk.Button(buttons, bg = BG, fg = FG, width = 10, text = "STOP", font = ("Cantarell", 20), command = stop)
    quit_button.grid(row = 0, column = 1, padx = 10, pady = 10)
   
    # Updating all labels
    def update():
        A = time.time()
        
        # Updating home labels
        for i in range(NUMBER_HOMES):
            if homes[i].energy.value <= 0 and homes[i].money.value < 1:
                house_labels[i].config(fg = "red")
                person_labels[i].config(fg = "red")
                name_labels[i].config(text = "-")
                policy_labels[i].config(text = "-")
                production_labels[i].config(text = "-")
                consumption_labels[i].config(text = "-")
                energy_labels[i].config(text = "-")
                money_labels[i].config(text = "-")
                continue
            elif homes[i].energy.value < homes[i].energy_min:
                house_labels[i].config(fg = "orange")
                person_labels[i].config(fg = "orange")
            elif homes[i].energy.value > homes[i].energy_min:
                house_labels[i].config(fg = "green")
                person_labels[i].config(fg = "green")
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

        window.after(round(UPDATE_RATE * 1000 / (24 * speed.value) - (time.time() - A)), update)

    update()
    window.mainloop()

