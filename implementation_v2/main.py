from random import randint, seed
import argparse
import cv2 as cv
import sys
import os
import math
import helper
import config
import numpy as np
import shutil

import cpu_search as cpu
import gpu_search as gpu

def test_func():
    print('scale factor: ', config.scale_factor)
    print('TPB: ', config.TPB)
    print('max value: ', config.UNEXPLORED)

def main():
    # check files, create and write headers if neccessary
    filename = os.path.join(os.getcwd(), 'implementation_v2/metrics/performance.csv')
    if os.path.isfile(filename) is False:
        with open(filename, "a") as file:
            file.write("image_filename,width,start,goal,cpu_runtime,gpu_runtime,cpu_path_exists,gpu_path_exists\n")

    from_file = open(filename)
    line = from_file.readline()
    line = "image_filename,width,start,goal,cpu_runtime,gpu_runtime,cpu_path_exists,gpu_path_exists\n"
    to_file = open(filename,mode="w")
    to_file.write(line)
    shutil.copyfileobj(from_file, to_file)

    parser = argparse.ArgumentParser(description='CPU vs GPU Pathfinding')
    parser.add_argument('scale_factor', type=int, help='Scale factor (power of 2)')
    parser.add_argument('TPB', type=int, help='Block width')
    parser.add_argument('complexity', type=str, help='Map Complexity')
    parser.add_argument('seed', type=str, help='RNG Seed', default=config.seed)
    args = parser.parse_args()
    config.scale_factor = args.scale_factor
    config.TPB = args.TPB
    config.padded_TPB = config.TPB + 2
    config.dim = int(math.pow(2, config.scale_factor)), int(math.pow(2, config.scale_factor))
    config.UNEXPLORED = int(math.pow(2, (config.scale_factor*2)))
    complexity = args.complexity
    config.seed = args.seed

    print('RNG Seed: ', config.seed)

    width, height = config.dim
    test_func()

    print('----- Preparing Grid -----')
    # create grid from image dataset
    grid = np.zeros(config.dim, dtype=np.int32)
    # helper.createGridFromDatasetImage('dataset/select-maps/simplest', grid, config.dim)
    image = helper.createGridFromDatasetImage('dataset/select-maps/%s'%(complexity), grid, config.dim)
    # grid = np.ones(config.dim, dtype=np.int32)

    # generate random start and goal
    start = [-1, -1]
    goal = [-1, -1]
    helper.randomStartGoal(grid, start, goal)
    # start = [0, 0]
    # goal = [grid.shape[0]-1, grid.shape[1]-1]
    start = np.array(start)
    goal = np.array(goal)
    
    print(grid)
    print(start)
    print(goal)

    helper.drawGrid(grid, tuple(start), tuple(goal))

    # cpu implementation
    runs_cpu, time_ave_cpu, path_cpu = cpu.test(grid, start, goal)
    # gpu implementation
    runs_gpu, time_ave_gpu, path_gpu = gpu.test(grid, start, goal)

    start_1d_index = start[0]*width+start[1]
    goal_1d_index = goal[0]*width+goal[1]

    print('----- Summary -----')
    print('Image used:', image)
    print('Start:', start)
    print('Goal:', goal)
    print()
    print('Average runtime in', runs_cpu, 'runs (CPU):', time_ave_cpu)
    print('path length (CPU):', len(path_cpu))
    print()
    print('Average runtime in', runs_gpu, 'runs (GPU):', time_ave_gpu)
    print('path length (GPU):', len(path_gpu))
    print()
    print('full path (CPU): ', path_cpu)
    print()
    print('full path (GPU): ', path_gpu)

    cpu_path_exists = path_cpu[0] == start_1d_index and path_cpu[-1] == goal_1d_index
    gpu_path_exists = len(path_gpu) > 0
    with open(os.path.join(os.getcwd(), 'implementation_v2/metrics/performance.csv'), "a") as log_file:
        log_file.write("{},{},{},{},{},{},{},{}\n".format(image, width, start, goal, time_ave_cpu, time_ave_gpu, cpu_path_exists, gpu_path_exists))



if __name__ == "__main__":
    main()