
import time

def calculate(num):
   lst = []
   for i in range(1, num + 1):
      if num % i == 0:
         lst.append(i)
   return lst

def factorize(*numbers):
   # result = tuple([] for _ in range(sz))
   # result = ([],)*sz

   sz = len(numbers)
   result = []

   for i in range(sz):
      lst = calculate(numbers[i])
      result.append(lst)

   return tuple(result)

if __name__ == "__main__":
   start = time.perf_counter()

   a, b, c, d = factorize(128, 255, 99999, 10651060)

   finish = time.perf_counter()

   assert a == [1, 2, 4, 8, 16, 32, 64, 128]
   assert b == [1, 3, 5, 15, 17, 51, 85, 255]
   assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
   assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 
      304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]

   print(f"OK: duration={round(finish-start, 3)}")
