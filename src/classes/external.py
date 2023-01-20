from multiprocessing import Process
 
class External(Process):

    def __init__(self):
        super().__init__()
        self.event = False 

    def run(self):
        print("External")
