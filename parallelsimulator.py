import multiprocessing as mp
from itertools import product
from os.path import  exists
from os import remove
from time import sleep


def do_work(arg, q):
    q.put("Processed parameter set {}".format(arg))

def record_results(q, file):
    while True:
        m = q.get()
        if m == 'kill':
            break
        with open(file, "a") as f:
            f.write(str(m) + '\n')
            print("writen to file.")



class ParallelSimulator:
    def __init__(self, results_file, parameter_space, max_queue_size=None, max_pool_size=None):
        self.results_file = results_file
        self.parameter_space = parameter_space
        self.manager = mp.Manager()
        if max_queue_size:
            self.output_queue = self.manager.Queue(maxsize=max_queue_size)
        else:
            self.output_queue = self.manager.Queue()

        if max_pool_size:
            self.work_pool = mp.Pool(max_pool_size)
        else:
            self.work_pool = mp.Pool()

    def shutdown(self):
        print("putting stoptoken in queue")
        self.output_queue.put("kill")
        print("shutting down workers")
        self.work_pool.close()
        self.work_pool.join()

    def start_work(self):
        if exists(self.results_file):
            remove(self.results_file)
        print("Starting recorder")
        # this must be apply_async because it has to work while the rest of the code continues
        self.work_pool.apply_async(record_results, (self.output_queue,self.results_file))

        print("Starting workers")
        self.work_pool.starmap(do_work, [(x, self.output_queue) for x in self.parameter_space])


if __name__ == "__main__":
    param_space = product(*[ range(3) for _ in range(3)])
    simulator = ParallelSimulator("parallel_results.txt", param_space)
    simulator.start_work()
    simulator.shutdown()
