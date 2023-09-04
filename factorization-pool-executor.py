from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool, current_process, cpu_count
import time

def calculate(num):
   name = current_process().name
   #print(f"calculate_{name}: {num}")
   lst = []
   for i in range(1, num + 1):
      if num % i == 0:
         lst.append(i)
   #print(f"calculate_{name} <<")
   return lst

def factorize(*numbers):
   result = []
   with ProcessPoolExecutor(cpu_count()) as executor:
      for num, lst in zip(numbers, executor.map(calculate, numbers)):
         result.append(lst)

   return tuple(result)


if __name__ == '__main__':
   print(f"Count CPU: {cpu_count()}")
   start = time.perf_counter()

   a, b, c, d = factorize(128, 255, 99999, 10651060)

   finish = time.perf_counter()

   print(a, b, c, d)

   assert a == [1, 2, 4, 8, 16, 32, 64, 128]
   assert b == [1, 3, 5, 15, 17, 51, 85, 255]
   assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
   assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 
      304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]

   print(f"OK: duration={round(finish-start, 3)}")
