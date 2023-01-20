from multiprocessing import Process
from classes.external import External
import time, socket, select, concurrent.futures


class Market(Process):

    HOST = "localhost"
    serve = True
    
    # Initialization of the market
    def __init__(self, port, P_0, max_threads):
        super().__init__()
        self.port = port
        self.P = P_0 
        self.max_threads = max_threads
    
    # Handling connections with homes
    def socket_handler(self, client_socket, address):
        global serve
        with client_socket:
            print("Connected to home: ", address)
            
            # Receiving what home wants to do
            action = client_socket.recv(1024).decode()[0]

            # Home wants to buy energy 
            if action == "1":

                # Sending the current price of 1 kWh of energy
                price = 4.23
                client_socket.send(str(price).encode())
                
                # Receiving the amount of energy needed by the home
                energy_needed = client_socket.recv(1024).decode()[0]
                if (energy_needed != "0"):
                    print("Transaction done:", energy_needed, "kWh bought for "+str(int(energy_needed)*price)+".")
                else:
                    print("No transaction done.")
            
            # Home wants to sell energy
            if action == "2":
                price = 4.5
                client_socket.send(str(price).encode())

        print("End of connection with home: ", address)
    
    # Main function
    def run(self):
        print("Market")
        
        # Lauching child process external
        external = External()
        external.start()

        # Socket handling with a pool of 'max_threads' threads
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setblocking(False)
            server_socket.bind((self.HOST, self.port))
            server_socket.listen(self.max_threads)
            with concurrent.futures.ThreadPoolExecutor(max_workers = self.max_threads) as executor:
                while self.serve:
                    readable, writable, error = select.select([server_socket], [], [], 1)
                    if server_socket in readable:

                        # If a home wants to connect
                        client_socket, address = server_socket.accept()
                        executor.submit(self.socket_handler, client_socket, address)
