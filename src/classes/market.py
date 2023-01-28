from multiprocessing import Process
from classes.external import External
import time, socket, select, concurrent.futures, signal, threading

STEP0 = 0.1
LOOP_DURATION = 1

def sum(l1, l2):
    sum = 0
    for i in range(len(l1)):
        sum += l1[i]*l2[i]
    return sum

class Market(Process):

    HOST = "localhost"
    EVENT_HANDLING = 0.05
    serve = True
    
    # Initialization of the market
    def __init__(self, port, temperature, price_0, max_threads):
        super().__init__()
        self.port = port
        self.temperature = temperature
        self.price = price_0 
        
        # Event handling
        self.max_threads = max_threads
        self.new_event = False
        self.event_counter = 0

        # Computations
        self.gamma = 0.9999
        self.alpha = [0.001, 0.0001]
        self.f = [0.0, 0.0]
        self.beta = [0.1, 0.3, 1, 3]
        self.u = [0, 0, 0, 0]

    
    # Handling connections with homes
    def socket_handler(self, client_socket, address):
        global serve
        with client_socket:
            print("[Market] Home connected:", address)
            
            # Receiving what home wants to do
            action = client_socket.recv(1024).decode()
            
            # Home wants to buy energy 
            if action == "1":
                client_socket.send(str(self.price).encode())
                self.f[1] += float(client_socket.recv(1024).decode())
            
            # Home wants to sell energy
            if action == "2":
                client_socket.send(str(self.price).encode())
                self.f[1] -= float(client_socket.recv(1024).decode())
            
            #print("[Market] Home disconnected:", address)
    
    def price_thread(self):
        while True:
            print(" ")
            # Random event handling
            t0 = time.time()
            start_time = 99999999999
            while (time.time() - t0 < STEP0):
                if self.new_event == True:
                    start_time = time.time()
                    self.new_event = False
                elif time.time() - start_time > self.EVENT_HANDLING:
                    self.u[self.event_counter - 1] = 1
                    self.event_counter = 0
                    start_time = 99999999999
            
            # Price update
            self.f[0] = 1/self.temperature.value
            self.price = self.gamma * self.price + sum(self.alpha, self.f) + sum(self.beta, self.u)
            self.u = [0, 0, 0, 0]
            self.f[1] = 0.0
            print("[Market]","{:.3f}".format(self.price), "€/kWh")
            time.sleep(1 - (time.time() - t0))

    # Main function
    def run(self):
        
        # Signal handling
        def handler(sig, frame):
            if sig == signal.SIGUSR1:
                self.new_event = True
            if sig == signal.SIGUSR2:
                self.event_counter += 1

        signal.signal(signal.SIGUSR1, handler) 
        signal.signal(signal.SIGUSR2, handler)

        # Lauching child process external
        external = External()
        external.start()

        price_handler = threading.Thread(target = self.price_thread)
        price_handler.start()

        # Socket handling with a pool of 'max_threads' threads
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setblocking(False)
            server_socket.bind((self.HOST, self.port))
            server_socket.listen(self.max_threads)
            with concurrent.futures.ThreadPoolExecutor(max_workers = self.max_threads) as executor:
                while self.serve:
                    # Connections handling
                    readable, writable, error = select.select([server_socket], [], [], 1)
                    if server_socket in readable:
                        # If a home wants to connect
                        client_socket, address = server_socket.accept()
                        executor.submit(self.socket_handler, client_socket, address)
