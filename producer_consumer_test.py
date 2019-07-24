# import multiprocessing as mp
#
# NCORE = 4
#
# def process(q, iolock):
#     while True:
#         stuff = q.get()
#         if stuff is None:
#             break
#         with iolock:
#             print("processing", stuff)
#
# if __name__ == '__main__':
#     q = mp.Queue(maxsize=NCORE)
#     iolock = mp.Lock()
#     pool = mp.Pool(NCORE, initializer=process, initargs=(q, iolock))
#     for stuff in range(20):
#         q.put(stuff)  # blocks until q below its max size
#         with iolock:
#             print("queued", stuff)
#     for _ in range(NCORE):  # tell workers we're done
#         q.put(None)
#     pool.close()
#     pool.join()


import multiprocessing as mp
from time import sleep


def worker(index, output_queue):
    result = "Processed index {}".format(index)
    output_queue.put(result)

def listener(q, file):
    while True:
        m = q.get()
        if m == 'kill':
            break
        with open(file, "a") as f:
            f.write(str(m) + '\n')
        print("writen to file.")





def main():
    #must use Manager queue here, or will not work
    file = "temp.txt"
    manager = mp.Manager()
    output_queue = manager.Queue(maxsize=5)
    pool = mp.Pool(mp.cpu_count())#,initializer=worker_init, initargs=(output_queue,))
    objects_to_process = range(20000)

    # this must be apply_async because it has to work while the rest of the code continues
    watcher = pool.apply_async(listener, (output_queue, file))

    pool.starmap(worker, [(x, output_queue) for x in objects_to_process])

    # wait until writer is done
    # while not output_queue.empty():
    #     sleep(2)
    # pool.close()
    output_queue.put("kill")
    # pool.close()

if __name__ == "__main__":
   main()