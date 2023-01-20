from multiprocessing import Process
import sys
import socket
 
class Home(Process):

    HOST = "localhost"

    # Initialization of a home
    def __init__(self, port, prod, cons, policy):
        super().__init__()
        self.port = port
        self.production = prod 
        self.consumption = cons
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
        self.market_interact()

