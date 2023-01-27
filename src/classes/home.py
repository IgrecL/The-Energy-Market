from multiprocessing import Process, Value
import sys, socket, time, sysv_ipc
 
class Home(Process):

    HOST = "localhost"
    LOOP_DURATION = 1
    STEP0 = 0.1
    STEP1 = 0.1
    STEP2 = 0.5
    STEP3 = 0.2
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
        t0 = time.time()
        while True:
            if (time.time() - t0 >= self.LOOP_DURATION):
                print(self.name, "---------------")
                self.manage_energy()
                t0 = time.time()

    def manage_energy(self):
        ti = time.time()
        self.energy += self.production - self.consumption
        time.sleep(self.STEP0 - (time.time() - ti)) 
        t0 = time.time()

        # Has too much energy
        if (self.energy > 0):

            if self.policy == 1:
                self.give1()
            t1 = time.time()
            time.sleep(self.STEP1 - (t1 - t0))

            t2 = time.time()
            if self.policy == 2:
                tk = time.time()
                while (tk - t2) < self.STEP2:
                    self.give2()
                    tk = time.time()

            if self.policy == 2 or self.policy == 3:
                self.sell()

        # Searching for free energy (policy 1)
        if (self.energy < 0):
            print(self.name, "I need", -self.energy, "kWh (step 1)")
            t1 = time.time()
            cont = True
            while (t1 - t0) < self.STEP1:
                if cont:
                    cont = self.get1()
                t1 = time.time()

        # Searching for free energy (policy 2) 
        if (self.energy < 0):
            print(self.name, "I need", -self.energy, "kWh (step 2)")
            t2 = time.time()
            cont = True
            while (t2 - t1) < self.STEP2:
                if cont:
                    cont = self.get2()
                t2 = time.time()

        # Buying to the market
        if (self.energy < 0):
            print(self.name, "Not enough free energy, I'll buy it from the market")
       
    # Giving energy for free to other homes
    def give1(self):
        print(self.name, "Sending ", self.energy, "kWh")
        self.queue.send(str(self.energy).encode(), type = 1)
        self.energy = 0
        print(self.name, "I now have", self.energy, "kWh")
    
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
            needed = int(m_list[1])
            print(self.name, "Received:", str(getter_id) + ":" + str(needed))

            # Sending the available energy to the home through its id
            if needed < self.energy:
                self.queue.send(str(needed).encode(), type = 10 + getter_id)
                self.energy -= needed
            else:
                self.queue.send(str(self.energy).encode(), type = 10 + getter_id)
                self.energy = 0

        # We have to retreive the packet if no one took it
        except sysv_ipc.BusyError:
            self.queue.receive(type = 2)

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

    def get1(self):
        try:
            m, t = self.queue.receive(block = False, type = 1)
            self.energy += int(m.decode())
            if self.energy >= 0:
                return False
            else:
                print(self.name, "Now I need", -self.energy, "kWh")
                return True
        except sysv_ipc.BusyError:
            return True

    def get2(self):
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
                return False
            else:
                print(self.name, "I need", -self.energy, "kWh")
                return True
        except:
            return True

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
