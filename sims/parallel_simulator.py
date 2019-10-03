import multiprocessing as mp
from os.path import exists
from os import remove

class ParallelSimulator:
    def __init__(self, results_file=None, parameter_space=None, max_queue_size=None, max_pool_size=None):
        self.results_file = results_file
        self.parameter_space = parameter_space
        self.manager = mp.Manager()
        self.max_queue_size = max_queue_size
        self.max_pool_size = max_pool_size

    def set_parameter_space(self, param_space):
        self.parameter_space = param_space

    def set_results_file(self, results_file):
        self.results_file = results_file

    def shutdown(self):
        print("putting stoptoken in queue")
        self.output_queue.put("kill")
        print("shutting down workers")
        self.work_pool.close()
        self.work_pool.join()

    def start_work(self, work_function, record_function):
        if not self.parameter_space:
            raise RuntimeError("cannot run without parameter_space")

        if not self.results_file:
            self.set_results_file("results/results.csv")

        if exists(self.results_file):
            remove(self.results_file)

        if self.max_queue_size:
            self.output_queue = self.manager.Queue(maxsize=self.max_queue_size)
        else:
            self.output_queue = self.manager.Queue()

        if self.max_pool_size:
            self.work_pool = mp.Pool(self.max_pool_size)
        else:
            self.work_pool = mp.Pool()

        print("Starting recorder")
        # this must be apply_async because it has to work while the rest of the code continues
        self.work_pool.apply_async(
            record_function, (self.output_queue, self.results_file))

        print("Starting workers")
        self.work_pool.starmap(
            work_function, [(x, self.output_queue) for x in self.parameter_space])

    def await_results(self):
        self.work_pool.join()



def do_work(arg, q):
    q.put("Processed parameter set {}".format(arg))


def record_results_as_csv(q, file, columns, chunksize=5):
    from pandas import DataFrame, Series # type
    from os.path import exists
    from os import remove
    counter = 0
    results = DataFrame(columns=columns)

    if exists(file):
        remove(file)

    while True:
        m = q.get()
        if m == 'kill':
            break
        counter += 1
        results = results.append(Series(m), ignore_index=True)

        if counter % chunksize == 0:
            results.to_csv(file, index=False)

    results.to_csv(file, index=False)
    print("recorder is dying....")