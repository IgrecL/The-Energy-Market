from multiprocessing import Process, Value
import sys, socket, time, sysv_ipc, random, threading

def digit(float):
    return "{:.2f}".format(round(float, 2))

class Home(Process):

    HOST = "localhost"
    
    # NUMBER_HOMES = 10
    WAITING1 = 0.1
    WAITING2 = 0.1
    ACK_TIME = 0.02

    # Initialization of a home
    def __init__(self, port, id, temperature, energy, money, prod, cons, policy):
        super().__init__()
        self.port = port
        self.id = id
        self.name = "[Home " + str(id) + "]"
        self.queue = sysv_ipc.MessageQueue(port)
        self.temperature = temperature
        self.energy = energy
        self.energy_max = 30
        self.energy_min = 10
        self.energy_margin = 10
        self.money = money
        self.production = prod 
        self.consumption = cons
        if (policy in range(1, 4)):
            self.policy = policy
        else:
            print("Choose a valid policy!")
            sys.exit(1)

    # Main function
    def run(self):
        update_thread = threading.Thread(target = self.update_thread)
        update_thread.start()
        t0 = time.time()
        timeout = random.uniform(1.0, 1.5)
        while True:
            if self.energy <= 0:
                print(self.name, "Dead")
                exit()
            if self.energy > self.energy_max and time.time() - t0 > timeout:
                self.give()
                t0 = time.time()
                timeout = random.uniform(1.0, 1.5)
            if self.energy < self.energy_min - 1:
                self.get()

    # Thread updating the energy each 'hour'
    def update_thread(self):
        while True:
            t0 = time.time()
            coeff = 1 + (15 - self.temperature.value)/100
            self.energy += self.production - coeff * self.consumption
            if 1/24 - (time.time() - t0) > 0:
                time.sleep(1/24 - (time.time() - t0))
        
    def give(self):
        if self.policy == 1:
            self.give1()

        if self.policy == 2:
            t0 = time.time()
            cont = True
            while cont and (time.time() - t0) < self.WAITING2:
                cont = self.give2()
            
        if self.policy == 2 or self.policy == 3:
            if self.energy - self.energy_max > 1:
                self.sell()



    def get(self):
        t0 = time.time()

        # Searching for free energy (policy 1)
        print(self.name, "I need", digit(self.energy_min - self.energy), "kWh (step 1)")
        t1 = time.time()
        cont = True
        while (t1 - t0) < self.WAITING1:
            if cont:
                cont = self.get1()
            t1 = time.time()

        # Searching for free energy (policy 2) 
        if (self.energy < self.energy_min):
            print(self.name, "I need", digit(self.energy_min - self.energy), "kWh (step 2)")
            t2 = time.time()
            cont = True
            while (t2 - t1) < self.WAITING2:
                if cont:
                    cont = self.get2()
                t2 = time.time()

        # Buying to the market
        if (self.energy < self.energy_min) and self.money > 0:
            #print(self.name, "Not enough free energy, I'll buy it from the market")
            self.buy()
       
    # Giving energy for free to other homes
    def give1(self):
        sent = self.energy - self.energy_max
        print(self.name, "Sending", digit(sent), "kWh")
        self.queue.send(str(sent).encode(), type = 1)
        self.energy -= sent
        print(self.name, "I now have", digit(self.energy), "kWh")
    
    # Giving energy for free if someone needs it
    def give2(self):
        self.queue.send(str(self.id).encode(), type = 2)
        time.sleep(self.ACK_TIME)

        # Checking whether someone responded
        try:
            m, t = self.queue.receive(block = False, type = 10 + self.id)
            print(self.name, "Someone wants my energy!")
            m_list = m.decode().split(":")
            getter_id = int(m_list[0])
            needed = float(m_list[1])
            print(self.name, "Received:", str(getter_id) + ":" + str(needed))

            # Sending the available energy to the home through its id
            if needed < self.energy - self.energy_max:
                self.queue.send(str(needed).encode(), type = 10 + getter_id)
                self.energy -= needed
                return True
            else:
                sent = self.energy - self.energy_max
                self.queue.send(str(sent).encode(), type = 10 + getter_id)
                self.energy -= sent 
                return False

        # We have to retreive the packet if no one took it
        except sysv_ipc.BusyError:
            self.queue.receive(type = 2)
            return False

    # Selling to the market
    def sell(self):
         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.HOST, self.port))
            client_socket.send(b"2")
            sold = self.energy - self.energy_max
            print(self.name, "I want to sell", digit(sold), "kWh")

            # Receiving energy price in €/kWh
            price = float(client_socket.recv(1024).decode())
            
            # Updating self.money
            client_socket.send(digit(sold).encode())
            print(self.name, digit(sold), "kWh sold for", digit(sold * price), "€")
            self.money += sold * price
            self.energy -= sold

    def get1(self):
        try:
            m, t = self.queue.receive(block = False, type = 1)
            self.energy += float(m.decode())
            if self.energy >= 0:
                return False
            else:
                print(self.name, "Now I need", digit(-self.energy), "kWh")
                return True
        except sysv_ipc.BusyError:
            return True

    def get2(self):
        try:
            # Checking if a home of policy 2 wants to know if someone needs energy 
            m, t = self.queue.receive(block = False, type = 2)
            giver_id = int(m.decode()) # The packet contains the id of the giver

            # Sending a request to this giver, with a header containing our id
            self.queue.send((str(self.id) + ":" + str(round(self.energy_min - self.energy, 2))).encode(), type = 10 + giver_id)
            print(self.name, "Sent info to home", giver_id)

            # Adding the energy received
            m, t = self.queue.receive(block = True, type = 10 + self.id)
            self.energy += float(m.decode())
            print(self.name, "Received", m.decode(), "kWh. I'm now at", digit(self.energy), "kWh")
            
            # Checking whether the given energy is enough
            if self.energy >= 0:
                return False
            else:
                print(self.name, "I need", digit(self.energy - self.energy), "kWh")
                return True
        except:
            return True

    # Buying to the market
    def buy(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.HOST, self.port))
            client_socket.send(b"1")
            
            # Receiving energy price in €/kWh
            price = float(client_socket.recv(1024).decode())

            # Sending kWh of energy needed
            bought = self.energy_margin if self.energy_margin * price < self.money else self.money / price
            client_socket.send(str(bought).encode())
            self.money -= bought * price
            print(self.name, "I bought", digit(bought), "kWh from the market for the price of", digit(bought * price), "€.")
            self.energy += bought
