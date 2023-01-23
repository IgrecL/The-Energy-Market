from multiprocessing import Process
import sys
import socket
 
class Home(Process):

    HOST = "localhost"

    # Initialization of a home
    def __init__(self, port, energy, money, prod, cons, policy):
        super().__init__()
        self.port = port
        self.energy = energy
        self.money = money
        self.production = prod 
        self.consumption = cons
        self.queues = []
        if (policy in range(1, 4)):
            self.policy = policy
        else:
            print("Choose a valid policy.")
            sys.exit(1)
   
    # Buying to the market
    def buy(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.HOST, self.port))
            client_socket.send(b"1")
            
            # Receiving energy price in €/kWh
            price = client_socket.recv(1024).decode()

            # Sending kWh of energy needed
            client_socket.send(str(self.energy).encode())
            self.money -= self.energy * int(price)
            self.energy = 0

    # Selling to the market
    def sell(self):
        if self.energy > 0:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.HOST, self.port))
                client_socket.send(b"2")
                print("I want to sell", self.energy, "kWh.")

                # Receiving energy price in €/kWh
                price = client_socket.recv(1024).decode()
                
                # Updating self.money
                client_socket.send(str(self.energy).encode())
                self.money += self.energy * float(price)
                self.energy = 0

    # Main function
    def run(self):
        print("Home")
        # self.market_interact()
        self.manage_energy()

    def give(self):
        for queue in self.queues:
            if self.energy > 0:
                print("J'ai", self.energy)
                queue[1].send(b"?")
                m, t = queue[0].receive()
                needed = int(m.decode())
                if (self.energy - needed >= 0):
                    queue[1].send(str(needed).encode())
                    self.energy -= needed
                else:
                    queue[1].send(str(self.energy).encode())
                    self.energy = 0
            else:
                queue[1].send(b"!")
            print("Il me reste", self.energy)


    def manage_energy(self):
        self.energy += self.production - self.consumption
        if (self.energy > 0):
            self.give_energy()
        elif (self.energy < 0):
            self.get_energy()

    def give_energy(self):
        if self.policy == 1 or self.policy == 2:
            self.give()
        if self.policy == 2 or self.policy == 3:
            self.sell()
                
    def get_energy(self):
        for queue in self.queues:
            print("Il me faut", self.energy)
            if self.energy < 0:
                m, t = queue[0].receive()
                if (m.decode() == "?"):
                    queue[1].send(str(-self.energy).encode())
                    m, t = queue[0].receive()
                    self.energy += int(m.decode())
            else:
                queue[0].receive()
            print("J'ai maintenant", self.energy)

