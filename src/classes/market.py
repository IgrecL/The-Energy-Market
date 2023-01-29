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
    def __init__(self, port, temperature, price, max_threads):
        super().__init__()
        self.port = port
        self.temperature = temperature
        self.price = price 
        
        # Event handling
        self.max_threads = max_threads
        self.sig1 = False
        self.event_counter = 0

        # Computations
        self.gamma = 0.9999
        self.alpha = [0.01, 0.00001]
        self.f = [0.0, 0.0]
        self.beta = [0.01, 0.03, 0.1, 0.3, 1]
        self.u = [0, 0, 0, 0, 0]

    # Main function
    def run(self):
        
        # Lauching child process external
        external = External()
        external.start()

        socket_thread = threading.Thread(target = self.socket_thread)
        price_thread = threading.Thread(target = self.price_thread)
        socket_thread.start()
        price_thread.start()
        
        # The main thread manages signals because a child thread cannot interpret signals
        # Signal 1 is used to signal a new event and signal 2 is used a counter
        def handler(sig, frame):
            if sig == signal.SIGUSR1:
                self.sig1 = True
            if sig == signal.SIGUSR2:
                self.event_counter += 1

        signal.signal(signal.SIGUSR1, handler) 
        signal.signal(signal.SIGUSR2, handler)

        # New event handling loop
        while True:
            if self.sig1:
                self.sig1 = False
                while not self.sig1:
                    pass
                self.u[self.event_counter - 1] = 1
                self.event_counter = 0
                self.sig1 = False

    # Thread managing connections with a thread pool of 'max_threads' threads 
    def socket_thread(self):
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
    
    # Handling connections with homes
    def socket_handler(self, client_socket, address):
        global serve
        with client_socket:
            #print("[Market] Home connected:", address)
            
            # Receiving what home wants to do
            action = client_socket.recv(1024).decode()
            
            # Home wants to buy energy 
            if action == "1":
                client_socket.send(str(self.price.value).encode())
                self.f[1] += float(client_socket.recv(1024).decode())
            
            # Home wants to sell energy
            if action == "2":
                client_socket.send(str(self.price.value).encode())
                self.f[1] -= float(client_socket.recv(1024).decode())
            
            #print("[Market] Home disconnected:", address)
    
    # Thread managing price changes
    def price_thread(self):
        while True:
            t0 = time.time()
            self.f[0] = 1/(self.temperature.value + 273.15)
            self.price.value = self.gamma * self.price.value + sum(self.alpha, self.f) + sum(self.beta, self.u)
            self.u = [0, 0, 0, 0, 0]
            self.f[1] = 0.0
            if self.price.value <= 0.01:
                self.price.value = 0.01
            #print("[Market]","{:.3f}".format(self.price.value), "€/kWh")
            if 1/24 - (time.time() - t0) > 0:
                time.sleep(1/24 - (time.time() - t0))
