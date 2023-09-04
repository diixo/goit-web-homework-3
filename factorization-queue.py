
from multiprocessing import Process, Queue, current_process, cpu_count, RLock, Value, Array
from ctypes import c_int
import logging
from array import array
import time

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def calculate(q_in: Queue, q_out: Queue):
   while not q_in.empty():
      lst = []
      num = q_in.get()
      for i in range(1, num + 1):
         if num % i == 0:
            lst.append(i)
      q_out.put(lst)
   return None


def factorize(*numbers):
   sz = len(numbers)

   queue_in = Queue()
   queue_out = Queue()
   _ = [queue_in.put_nowait(v) for v in numbers]

   processes = []
   for i in range(sz):
      pr = Process(target=calculate, args=(queue_in, queue_out,))
      pr.start()
      processes.append(pr)

   [pr.join() for pr in processes]
   queue_out.put(None)  # add last element=None as marker

   return tuple(item for item in iter(queue_out.get, None))
   #return tuple(list(iter(queue_out.get, None)))


if __name__ == "__main__":
   print(f"Count CPU: {cpu_count()}")
   start = time.perf_counter()

   a, b, c, d = factorize(128, 255, 99999, 10651060)

   finish = time.perf_counter()

   print(f"{a}\n{b}\n{c}\n{d}")

   assert a == [1, 2, 4, 8, 16, 32, 64, 128]
   assert b == [1, 3, 5, 15, 17, 51, 85, 255]
   assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
   assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 
      304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]

   print(f"OK: duration={round(finish-start, 3)}")
