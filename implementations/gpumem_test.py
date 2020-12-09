TPB = 2

from numba import cuda, int32
import numpy as np
import cupy as cp
import math

@cuda.jit
def gpu_memory_test(arr):
    x, y = cuda.grid(2)
    width, height = arr.shape
    tx = cuda.threadIdx.x
    ty = cuda.threadIdx.y
    bx = cuda.blockIdx.x
    by = cuda.blockIdx.y
    dim_x = cuda.blockDim.x
    dim_y = cuda.blockDim.y
    bpg_x = cuda.gridDim.x
    bpg_y = cuda.gridDim.y
    bpg = bpg_x

    # print(bpg)
    if x >= arr.shape[0] and y >= arr.shape[1]:
        return

    # shared_arr = cuda.shared.array(shape=(TPB, TPB), dtype=int32)
    # shared_arr[tx,ty] = arr[tx, ty]
    # cuda.syncthreads()
    # arr[tx,ty] = shared_arr[tx, ty]*2
    # cuda.syncthreads()

    arr[x, y, 0] = bx
    arr[x, y, 1] = by

def main():
    arr = np.zeros(shape=(8,8,2), dtype=np.int32)
    arr_gpu = cp.zeros(shape=(8,8,2), dtype=cp.int32)

    w, h = arr.shape
    for i in range(w):
        for j in range(h):
            arr[i,j] = np.array([i,j])

    print(arr)

    threadsperblock = (TPB, TPB)
    blockspergrid_x = math.ceil(arr.shape[0] / threadsperblock[0])
    blockspergrid_y = math.ceil(arr.shape[1] / threadsperblock[1])
    blockspergrid = (blockspergrid_x, blockspergrid_y)
    gpu_memory_test[blockspergrid, threadsperblock](arr)

    print(arr)
    # print(arr_gpu)

if __name__ == "__main__":
    main()