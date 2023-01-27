from multiprocessing import Process
from classes.external import External
import time, socket, select, concurrent.futures, signal

def sum(l1, l2):
    sum = 0
    for i in range(len(l1)):
        sum += l1[i]*l2[i]
    return sum

class Market(Process):

    HOST = "localhost"
    serve = True
    
    # Initialization of the market
    def __init__(self, port, temperature, P_0, max_threads):
        super().__init__()
        self.port = port
        self.temperature = temperature
        self.P = P_0 
        
        # Event handling
        self.max_threads = max_threads
        self.new_event = False
        self.event_counter = 0

        # Computations
        self.t = 0
        self.gamma = 0.9999
        self.alpha = [0.001, 0.01]
        self.f = [0, 0]
        self.beta = [0.1, 0.3, 1, 3]
        self.u = [0, 0, 0, 0]

    
    # Handling connections with homes
    def socket_handler(self, client_socket, address):
        global serve
        with client_socket:
            print("[Market] Home connected:", address)
            
            # Receiving what home wants to do
            action = client_socket.recv(1024).decode()[0]

            # Home wants to buy energy 
            if action == "1":
                client_socket.send(str(self.P).encode())
                energy_needed = client_socket.recv(1024).decode()[0]
            
            # Home wants to sell energy
            if action == "2":
                client_socket.send(str(self.P).encode())
                energy_sold = client_socket.recv(1024).decode()

        print("[Market] Home Disconnected:", address)
    
              
    # Main function
    def run(self):
        
        # Signal hanler
        def handler(sig, frame):
            if sig == signal.SIGUSR1:
                self.new_event = True
            if sig == signal.SIGUSR2:
                self.event_counter += 1

        # Lauching child process external
        #external = External()
        #external.start()
        
        # Random events
        # signal.signal(signal.SIGUSR1, handler) 
        #signal.signal(signal.SIGUSR2, handler)
        #start_time = 99999999999
        #while True:
        #    if self.new_event == True:
        #        start_time = time.time()
        #        self.new_event = False
        #    elif time.time() - start_time > 0.1:
        #        for i in range(4):
        #            if self.event_counter == i:
        #                self.u[i - 1] = 1
        #        self.event_counter = 0
        #        start_time = 99999999999
        #    self.P = self.gamma*self.P + sum(self.alpha, self.f) + sum(self.beta, self.u)
        #    self.u = [0, 0, 0, 0]
        #    #if self.t % 24 == 0:
        #    #    print("[Market] " + "{:.3f}".format(self.P) + "€/kWh (day " + str(int(self.t/24)) + ")")
        #    self.t += 1
        #    time.sleep(1/24)

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
