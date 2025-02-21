import os
import numpy as np
from tqdm import tqdm


#take all csv files in a folder (formatted by header and data) and convert them to numpy arrays

dirr = 'in_data'

files = os.listdir(dirr)
files = [dirr + '/' + f for f in files if f.endswith('.csv')]
files = [f for f in files if "+" not in f and "_len" not in f]

#process
for file_in in files:
    print(file_in)
    #first see if len is available
    file_len_meta = file_in.replace('.csv', '_len.csv')
    if os.path.exists(file_len_meta):
        print("len file exists")
        with open(file_len_meta, "r") as f:
            total_points = int(f.read())
    else:
        print("Estimating len and generating len file")
        with open(file_in, "rb") as f:
            #num_lines = len(f.readlines())
            num_lines = np.sum(np.fromiter((1 for _ in tqdm(f)), dtype=np.int32))
            """i = 0
            for line in f:
                if i == 1:
                    typical_line = line
                    break
                i += 1
            #in a standard csv format, how many bytes are in a line
            bytes_per_line = len(typical_line)
            total_file_size = os.path.getsize(file_in)
            num_lines = total_file_size / bytes_per_line
        total_points = int(num_lines)#!guesstimate"""
        total_points = num_lines - 1
        with open(file_len_meta, "w") as f:
            f.write(str(total_points))
    print("Total points: ", total_points)
    #next, find width of arr
    exclude_colls = [0,1]
    with open(file_in, "r") as f:
        header = f.readline().strip().split(',')
        header = [h for i,h in enumerate(header) if i not in exclude_colls]
        width = len(header)
    print("Width: ", width)
    #now, create the array, and have it directly memmory mapped
    #arr = np.memmap(file_in.replace('.csv', '.npy'), dtype=np.float32, mode='w+', shape=(total_points, width))
    dummy = np.zeros((total_points, width), dtype=np.float32)
    np.save(file_in.replace('.csv', '.npy'), dummy)
    del dummy
    arr = np.load(file_in.replace('.csv', '.npy'), mmap_mode='r+')
    #fill the array
    with open(file_in, "r") as f:
        f.readline()
        for i, line in tqdm(enumerate(f), total=total_points):
            line = line.strip().split(',')
            line = [float(l) for i,l in enumerate(line) if i not in exclude_colls]
            if i % 1000000 == 0:
                if i == 0:
                    continue
                #test for rounding error when mapping to float32
                for num in line:
                    num_32 = np.float32(num)
                    #given that it is integer data, see if the rounding error is less than 1
                    if abs(num - num_32) > 0.1:
                        print("Rounding error detected: ", num, num_32)
            arr[i] = line
        #write the shape to a file
        with open(file_in.replace('.csv', '_shape.txt'), "w") as f:
            f.write(str(arr.shape))