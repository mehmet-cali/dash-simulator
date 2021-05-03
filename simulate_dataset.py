import dash_stream_simulator
import copy
import scipy.io
import numpy as np
import timeit
import os

#simulate the algorithms for the dash datasets(ssim and file_size) specified in dirs and outputs to output_base
#You should run this file first by setting adapt_list
#if you need single adaptation performance, you need to set adapt_list=[<n>] for algorithm<n>
#After running this script you should run average_results.m Matlab file

def simulate_datasets(adapt_list,dataset_base,output_base,dirs,sizes,ssim):
    for i in dirs:
        path_i1=dataset_base+i+ssim
        path_i2 = dataset_base + i + sizes
        out_path=output_base+i+output_base[:-1]
        dash_stream_simulator.simulate(adapt_list,path_i1,path_i2,out_path)

def save_overall(adapt_list):
    dataset_base = "dataset_info/"
    output_base = "sim_results/"
    dirs = ["vbr/bbb/", "vbr/tos/", "vbr/sintel/", "cbr/bbb/", "cbr/tos/", "cbr/sintel/"]
    sizes = "sizes.csv"
    ssim = "ssim.csv"
    simulate_datasets(adapt_list,dataset_base,output_base,dirs,sizes,ssim)


def main():
    start = timeit.default_timer()
    #Adjust the adapt_list according to which functions you want to simulate
    adapt_list = [1, 2]
    save_overall(adapt_list)
    end = timeit.default_timer()
    print("Overall run time: " + str(end - start))


if __name__=="__main__":
    main()
