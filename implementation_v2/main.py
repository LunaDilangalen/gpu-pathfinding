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
    filename = os.path.join(os.getcwd(), 'implementation_v2/metrics/data/performance.csv')
    if os.path.isfile(filename) is False:
        with open(filename, "w") as file:
            file.write("image,grid_width,block_width,start,goal,cpu_runtime,gpu_runtime,cpu_path_length,gpu_path_length,cpu_path_exists,gpu_path_exists\n")

    from_file = open(filename)
    line = from_file.readline()
    line = "image,grid_width,block_width,start,goal,cpu_runtime,gpu_runtime,cpu_path_length,gpu_path_length,cpu_path_exists,gpu_path_exists\n"
    to_file = open(filename,mode="w")
    to_file.write(line)
    from_file.close()
    to_file.close()
    
    parser = argparse.ArgumentParser(description='CPU vs GPU Pathfinding')
    parser.add_argument('scale_factor', type=int, help='Scale factor (power of 2)')
    parser.add_argument('TPB', type=int, help='Block width')
    parser.add_argument('complexity', type=str, help='Map Complexity')
    # parser.add_argument('heuristics', type=str, help='Heuristic')
    # parser.add_argument('seed', type=int, help='RNG Seed', default=config.seed)
    parser.add_argument('runs', type=int, help='Test run count', default=100)
    args = parser.parse_args()
    config.scale_factor = args.scale_factor
    config.TPB = args.TPB
    config.padded_TPB = config.TPB + 2
    config.dim = int(math.pow(2, config.scale_factor)), int(math.pow(2, config.scale_factor))
    config.UNEXPLORED = int(math.pow(2, (config.scale_factor*2)))
    complexity = args.complexity
    # heuristics = args.heuristics
    # heuristics_choices = {'euclidean':0, 'diagonal':1, 'manhattan':2}
    # config.heuristics = heuristics_choices[heuristics]
    print(config.heuristics)
    runs = args.runs
    # config.seed = args.seed

    possible_scale_factors = list(range(4,11))
    possible_TPBs = [4,8,16]

    for i in range(runs):
        print('===== %dth Test =====' %(i))
        width, height = config.dim
        # test_func()

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
        start_1d_index = start[0]*width+start[1]
        goal_1d_index = goal[0]*width+goal[1]

        print(grid)
        print(start)
        print(goal)

        helper.drawGrid(grid, tuple(start), tuple(goal))

        # cpu implementation
        runs_cpu, time_ave_cpu, path_cpu = cpu.test(grid, start, goal)
        path_length_cpu = len(path_cpu)
        path_exists_cpu = path_cpu[0] == start_1d_index and path_cpu[-1] == goal_1d_index
        # gpu implementation
        runs_gpu, time_ave_gpu, path_gpu = gpu.test(grid, start, goal)
        path_length_gpu = len(path_gpu)
        path_exists_gpu = path_length_gpu > 0
        # summarize info
        print('----- Summary -----')
        # general info
        print('Image used:', image)
        print('Start:', start)
        print('Goal:', goal)
        print()
        # cpu info
        print('search runtime (CPU):', time_ave_cpu )
        print('path length (CPU):', len(path_cpu))
        print()
        print('search runtime (GPU):', time_ave_gpu)
        print('path length (GPU):', path_length_gpu)
        print()

        with open(os.path.join(os.getcwd(), 'implementation_v2/metrics/data/performance.csv'), "a") as log_file:
            log_file.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(image, width, config.TPB, start_1d_index, goal_1d_index, time_ave_cpu, time_ave_gpu, path_length_cpu, path_length_gpu, path_exists_cpu, path_exists_gpu))



if __name__ == "__main__":
    main()