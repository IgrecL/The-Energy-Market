from multiprocessing import Process
import sys
import socket
 
class Home(Process):

    HOST = "localhost"

    # Initialization of a home
    def __init__(self, port, energy, prod, cons, policy):
        super().__init__()
        self.port = port
        self.energy = energy
        self.production = prod 
        self.consumption = cons
        self.queues = []
        if (policy in range(3)):
            self.policy = policy
        else:
            print("Choose a valid policy.")
            sys.exit(1)
   
    # Choice of action
    def choice(self):
        answer = 1
        return answer
    
    # Buying and selling to the market
    def market_interact(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            
            # TCP connection with the market
            client_socket.connect((self.HOST, self.port))
            
            # Whether buying or selling energy
            action = self.choice()

            # Buying energy
            if action == 1:
                client_socket.send(b"1")
                
                # Receiving energy price by kWh
                price = client_socket.recv(1024)
                if not len(price):
                    print("The socket connection has been closed!")
                    sys.exit(1)
                price = price.decode()
                
                # Sending kWh of energy needed
                energy_needed = 4
                client_socket.send(str(energy_needed).encode())

            # Selling energy
            if action == 2:
                client_socket.send(b"2")


    # Main function
    def run(self):
        print("Home")
        # self.market_interact()
        self.manage_energy()

    def manage_energy(self):
        self.energy += self.production - self.consumption
        if (self.energy > 0):
            self.give_energy()
        elif (self.energy < 0):
            self.get_energy()

    def give_energy(self):
        if self.policy == 1:
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

