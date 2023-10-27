from operator import index
import numpy as np
import time

N = 65536
arr = np.arange(10001, 10001 + N + 1)
rng = np.random.default_rng()
rand_port = 10001 + rng.integers(N, size=1000)
print(rand_port)
time_start = 0
time_end = 0

for p in rand_port:
    print("Searching...")
    time_start = int(round(time.time() * 1000))
    np.random.shuffle(arr)
    # for a in arr:
    #     if a == p:
    #         break
    #     time.sleep(0.2)
    time_end = int(round(time.time() * 1000))
    f = open("time.txt", "a")
    f.write(str(int(time_end - time_start)) + "\n")
    f.close()

    # f = open("time.txt", "a")
    # f.write(str(int(0.2* (np.where(arr == p)[0][0] + 1))) + "\n")
    # f.close()

    # i = 0
    # while True:
    #     a = 10001 + rng.integers(N, size=1)
    #     # print(a)
    #     if a == p:
    #         break
    #     i += 1
    # f = open("time.txt", "a")
    # f.write(str(int(0.2* (i + 1))) + "\n")
    # f.close()

