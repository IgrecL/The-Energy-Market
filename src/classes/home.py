from multiprocessing import Process, Value
import socket, time, sysv_ipc, random, threading

HOST = "localhost"
PORT = 1566

def digit(float):
    return "{:.2f}".format(round(float, 2))

class Home(Process):

    TRANSACTION = 0.02
    
    # Prints a message to the GUI log
    def log(self, msg):
        self.print.send(("[Home " + str(self.id) + "] " + msg).encode())

    # Initialization of a home
    def __init__(self, id, temperature, energy, money, people, cons, policy):
        super().__init__()
        
        # Parameters
        self.id = id
        self.queue = sysv_ipc.MessageQueue(600)
        self.print = sysv_ipc.MessageQueue(700)
        self.policy = policy
        
        # Shared values
        self.temperature = temperature
        self.energy = energy
        self.money = money
        
        # Energy management
        self.stop = False
        self.production = people * 0.5 
        self.consumption = cons
        self.energy_max = 30
        self.energy_min = 10
        self.energy_margin = 10

    # Main function
    def run(self):
        update_thread = threading.Thread(target = self.update_thread)
        update_thread.start()
        t0 = time.time()
        timeout = random.uniform(0.5, 1.5)
        while True:
            if self.energy.value <= 0:
                self.log("I am dead")
                self.stop = True
                update_thread.join()
                exit(1)
            if self.energy.value > self.energy_max and time.time() - t0 > timeout:
                t0 = time.time()
                self.give(timeout)
                timeout = random.uniform(0.5, 1.5)
            if self.energy.value < self.energy_min - 1:
                self.get()

    # Thread updating the energy each 'hour'
    def update_thread(self):
        while not self.stop:
            t0 = time.time()
            if self.energy.value > 0:
                coeff = 1 + (15 - self.temperature.value)/100
                self.energy.value += self.production - coeff * self.consumption
            if 1/24 - (time.time() - t0) > 0:
                time.sleep(1/24 - (time.time() - t0))
        
    def give(self, timeout):
        if self.policy == 1:
            self.give1()

        if self.policy == 2:
            self.give2(timeout)
            
        if self.policy == 2 or self.policy == 3:
            if self.energy.value - self.energy_max > 1:
                self.sell()

    def get(self):
        # Searching for free energy (policy 1)
        self.get1()

        # Searching for free energy (policy 2) 
        if (self.energy.value < self.energy_min):
            t0 = time.time()
            enough = False
            while not enough and time.time() - t0 < random.uniform(0.5, 1.0):
                enough = self.get2()

        # Buying to the market
        if (self.energy.value < self.energy_min) and self.money.value > 0:
            self.buy()
       
    # Giving energy for free to other homes
    def give1(self):
        sent = self.energy.value - self.energy_max
        self.queue.send(str(sent).encode(), type = 1)
        self.log("I sent " + digit(sent) + " kWh for free")
        self.energy.value -= sent
    
    # Giving energy for free if someone needs it
    def give2(self, timeout):
        t0 = time.time()
        while time.time() - t0 < timeout - self.TRANSACTION:
            self.queue.send(str(self.id).encode(), type = 2)
            received = False

            # Waiting for someone to respond or timeout
            while not received and time.time() - t0 < timeout - self.TRANSACTION:
                try:
                    m, t = self.queue.receive(block = False, type = 10 + self.id)
                    m_list = m.decode().split(":")
                    getter_id = int(m_list[0])
                    needed = float(m_list[1])

                    # Sending the available energy to the home through its id
                    if needed < self.energy.value - self.energy_max:
                        sent = needed
                    else:
                        sent = self.energy.value - self.energy_max
                    self.queue.send(str(needed).encode(), type = 10 + getter_id)
                    self.energy.value -= needed
                    self.log("I sent " + digit(sent) + " kWh to Home " + str(getter_id))
                    received = True
                except sysv_ipc.BusyError:
                    pass

            if not received:
                self.queue.receive(type = 2)

    # Selling to the market
    def sell(self):
         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            client_socket.send(b"2")
            sold = self.energy.value - self.energy_max

            # Receiving energy price in €/kWh
            price = float(client_socket.recv(1024).decode())
            
            # Updating self.money
            client_socket.send(digit(sold).encode())
            self.money.value += sold * price
            self.energy.value -= sold
            self.log("I sold " + digit(sold) + " kWh to the market for " + digit(sold * price) + " €")

    def get1(self):
        try:
            m, t = self.queue.receive(block = False, type = 1)
            self.energy.value += float(m.decode())
            self.log("I got " + digit(float(m.decode())) + " kWh for free")
            return False if self.energy.value >= 0 else True
        except sysv_ipc.BusyError:
            return True

    def get2(self):
        try:
            # Checking if a home of policy 2 wants to know if someone needs energy 
            m, t = self.queue.receive(block = False, type = 2)
            giver_id = int(m.decode()) # The packet contains the id of the giver

            # Sending a request to this giver, with a header containing our id
            self.queue.send((str(self.id) + ":" + digit(self.energy_min - self.energy.value + 1)).encode(), type = 10 + giver_id)

            # Adding the energy received
            m, t = self.queue.receive(block = True, type = 10 + self.id)
            self.energy.value += float(m.decode())
            self.log("I got " + digit(float(m.decode())) + " kWh from Home " + str(giver_id))
            
            # Checking whether the given energy is enough
            return True if self.energy.value >= self.energy_min else False
        except:
            return False

    # Buying to the market
    def buy(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            client_socket.send(b"1")
            
            # Receiving energy price in €/kWh
            price = float(client_socket.recv(1024).decode())

            # Sending kWh of energy needed
            bought = self.energy_margin if self.energy_margin * price < self.money.value else self.money.value / price
            client_socket.send(str(bought).encode())
            self.money.value -= bought * price
            self.energy.value += bought
            self.log("I bought " + digit(bought) + " kWh from the market for " + digit(bought * price) + " €")
