from multiprocessing import Process, Value
import sys, socket, time, sysv_ipc
 
class Home(Process):

    HOST = "localhost"
    WAITING_TIME = 0.1
    BUYING_TIME = 0.012
    ACK_TIME = 0.01

    # Initialization of a home
    def __init__(self, port, id, temperature, energy, money, prod, cons, policy):
        super().__init__()
        self.port = port
        self.id = id
        self.name = "[Home " + str(id) + "]"
        self.queue = sysv_ipc.MessageQueue(port)
        self.temperature = temperature
        self.energy = energy
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
        #for t in range(9999999):
        #    # print(self.name,  "Temperature : " + "{:.1f}".format(self.temperature.value) + "°C")
        #    time.sleep(1)
        while True:
            self.manage_energy() # Lasts WAITING_TIME + BUYING_TIME
            time.sleep(3 - self.WAITING_TIME - self.BUYING_TIME)

    def manage_energy(self):
        self.energy += self.production - self.consumption
        
        # Has too much energy
        if (self.energy > 0):
            if self.policy == 1 or self.policy == 2:
                self.give(self.energy)
                time.sleep(self.WAITING_TIME + self.BUYING_TIME)
            elif self.policy == 3:
                self.sell()

        # Needs energy
        elif (self.energy < 0):
            time.sleep(self.WAITING_TIME)
            self.get()

        else:
            print(self.name, "Nothing")
    
    # Giving energy for free to other homes
    def give(self, amount):
        if self.policy == 1:
            print(self.name, "Sending ", amount, "kWh")
            self.queue.send(str(self.energy).encode(), type = 1) # Energy giveaway
            self.energy = 0
            print(self.name, "I now have", self.energy, "kWh")
        if self.policy == 2:
            # Asking if someone needs energy
            print(self.name, "Who wants energy?")
            self.queue.send(str(self.id).encode(), type = 2)
            time.sleep(self.WAITING_TIME + self.ACK_TIME)

            # Checking whether someone responded
            cont = True
            while cont:
                try:
                    m, t = self.queue.receive(block = False, type = 10 + self.id)
                    m_list = m.decode().split(":")
                    getter_id = int(m_list[0])
                    needed = int(m_list[1])
                    print(self.name, "Received:", str(getter_id) + ":" + str(needed))

                    # Sending the available energy to the home through its id
                    if needed < self.energy:
                        self.queue.send(str(needed).encode(), type = 10 + getter_id)
                    else:
                        self.queue.send(str(self.energy).encode(), type = 10 + getter_id)
                except sysv_ipc.BusyError:
                    cont = False

    # Selling to the market
    def sell(self):
        if self.energy > 0:
             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.HOST, self.port))
                client_socket.send(b"2")
                print(self.name, "I want to sell", self.energy, "kWh")

                # Receiving energy price in €/kWh
                price = float(client_socket.recv(1024).decode())
                
                # Updating self.money
                client_socket.send(str(self.energy).encode())
                print(self.name, self.energy, "kWh sold for "+str(int(self.energy*price))+"€")
                self.money += self.energy * price
                self.energy = 0

    # Get energy from other homes 
    def get(self):
        print(self.name, "I need", -self.energy, "kWh")
        
        # Loop for free energy 
        cont = True
        while cont:
            try:
                m, t = self.queue.receive(block = False, type = 1)
                self.energy += int(m.decode())
                if self.energy >= 0:
                    time.sleep(self.BUYING_TIME)
                    cont = False
                else:
                    print(self.name, "Now I need", -self.energy, "kWh")
            except sysv_ipc.BusyError:
                cont = False
        
        # Loop for energy given by homes of policy 2 if not enough energy
        cont = (self.energy < 0)
        while cont:
            try:
                # Checking if a home of policy 2 wants to know if someone needs energy 
                m, t = self.queue.receive(block = False, type = 2)
                giver_id = int(m.decode()) # The packet contains the id of the giver

                # Sending a request to this giver, with a header containing our id
                self.queue.send((str(self.id) + ":" + str(-self.energy)).encode(), type = 10 + giver_id)
                print(self.name, "Sent info to home", giver_id)

                # Adding the energy received
                m, t = self.queue.receive(block = True, type = 10 + self.id)
                self.energy += int(m.decode())
                print(self.name, "Received", m.decode(), "kWh. I'm now at", self.energy, "kWh")
                
                # Checking whether the given energy is enough
                if self.energy >= 0:
                    time.sleep(self.BUYING_TIME)
                    cont = False
                else:
                    print(self.name, "I need", -self.energy, "kWh")
            except:
                cont = False
        
        # If home still needs energy, buying to the market
        if self.energy < 0:
            print(self.name, "Pas assez d'énergie gratuite, j'achète au market")
            self.buy()

    # Buying to the market
    def buy(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.HOST, self.port))
            client_socket.send(b"1")
            
            # Receiving energy price in €/kWh
            price = client_socket.recv(1024).decode()

            # Sending kWh of energy needed
            client_socket.send(str(self.energy).encode())
            self.money -= self.energy * float(price)
            print(self.name, "J'ai acheté", -self.energy, "kWh au marché au prix de", price, "€.")
            self.energy = 0
