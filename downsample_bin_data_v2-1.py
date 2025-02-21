# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 10:40:13 2024

@author: Philipp Wunderl (philipp.wunderl@tum.de)
"""

import numpy as np
import gc
import os
import subprocess
import shutil
from natsort import natsorted 
import matplotlib.pyplot as plt
from scipy.signal import decimate
#from numba import jit
from copy import deepcopy as copy
import dbm
import fileinput
import dask.dataframe as dd
from numba import jit
from scipy.signal import resample
from tqdm import tqdm






#%%

###############################
####### Can be adjusted #######

# Path to directory with data  (file ...\rawdata_...)
data_path ='in_data/'
# Path for saving downsampled data
path = 'prepped_data/'

num_ch = 2  # Number of channels
freq = 1000  # Sampling frequency
target_fs = 50  # Target sampling frequency after downsampling
max_memory_usage_mb = 250  # Maximum memory usage of loaded bin data in MB 
conversion_factor = 0.0001331253868
block_size_mb = 250  # Size of each block to be saved in MB
mag_data=True #Convert voltage values to muT -> conversion factors depend on the fluxgate type; if False the voltage values are saved
name = "Fieldline_" #name of the measurement 

###################################
###################################
class FileDict:
    def __init__(self, filename):
        self.filename = filename

    def __getitem__(self, key):
        with open(self.filename, 'r') as f:
            for line in f:
                k, v = line.strip().split('=', 1)
                if k == key:
                    return v
        raise KeyError(key)

    def __setitem__(self, key, value):
        lines = []
        found = False
        # Read and update if the key exists
        with open(self.filename, 'r') as f:
            for line in f:
                k, v = line.strip().split('=', 1)
                if k == key:
                    lines.append(f"{key}={value}\n")
                    found = True
                else:
                    lines.append(line)
        # Append new key-value if key not found
        if not found:
            lines.append(f"{key}={value}\n")
        # Write back to the file
        with open(self.filename, 'w') as f:
            f.writelines(lines)

    def __delitem__(self, key):
        lines = []
        found = False
        with open(self.filename, 'r') as f:
            for line in f:
                k, v = line.strip().split('=', 1)
                if k == key:
                    found = True
                else:
                    lines.append(line)
        if not found:
            raise KeyError(key)
        with open(self.filename, 'w') as f:
            f.writelines(lines)

    def __iter__(self):
        with open(self.filename, 'r') as f:
            for line in f:
                yield line.strip().split('=', 1)[0]

    def keys(self):
        return list(iter(self))

"""# Usage with an existing file
file_dict = FileDict('existing_file.txt')

# Accessing
print(file_dict['key1'])

# Modifying
file_dict['key1'] = 'new_value'

# Adding
file_dict['key3'] = 'value3'

# Iterating
for key in file_dict:
    print(key)"""



def find_files(datapath):
    list_of_files = []
    for root, dirs, files in os.walk(datapath):
        for file in files:
            if "0" in file and "Test" not in root:
                full_path = os.path.join(root, file)
                if "len" not in full_path:
                    list_of_files.append(full_path)
    list_of_files = [f for f in list_of_files if "fuse" not in f]
    list_of_files = [f for f in list_of_files if ".npy" in f]
    return natsorted(list_of_files)

"""def load_bin_data_chunked(file, start_idx, num_points, num_ch, file_len):

    #db = FileDict(file)
    #db = dd.read_csv(file)
    channels_key = [
        'Dev0-18',
        'Dev1-18'
    ]
    channels_key = channels_key[:num_ch]#!temp
    #data_chunk = np.zeros((num_ch, num_points), dtype=float)

    
    
    header_lines = 1
    s = header_lines# + start_idx
    data_chunk = np.full((num_ch, num_points),np.nan, dtype=float)
    #with open(file, 'r') as f:
        #lines = 
    #for i, line in tqdm(enumerate(f.readlines()), total=num_points):
    i = -1
    #search for +'s in dir, and load the one with the highest number
    dirr = os.path.dirname(file)
    files = os.listdir(dirr)
    files = [f for f in files if f.endswith(".csv")]
    files = [f for f in files if f.startswith(os.path.basename(file).replace(".csv", "_+"))]
    if len(files) == 0:
        pass
    else:
        files = natsorted(files)
        file = os.path.join(dirr, files[-1])
    plusCnt = file.count("+")
    file_np1 = file.replace(".csv", "_+.csv")
    with open(file_np1, 'w') as f_np1:
        with open(file, 'r') as f:
            print(f"Reading chunk of {num_points} data points from file {file} starting at index {s}")
            for line in tqdm(f, total=num_points, desc="Loading data", unit="lines", mininterval=0.5):
                i += 1
                if i < s:
                    f_np1.write(line)
                    continue
                if i == s + num_points:
                    print(f"Reached end of chunk at line {i}, starting to write rest of file")
                    write_mode = True
                    #read and write the rest of the file in chuncks
                    l = line
                    while l:
                        f_np1.write(l)
                        l = f.readline()
                    break
                
                line = line.strip().split(',')
                if len(line) < num_ch + 2:
                    print(f"Warning, data point {i} has only {len(line)-2} values")
                    continue
                j = i - header_lines
                data_chunk[:, j] = np.array(line[2:], dtype=float)
            f.close()
        f_np1.close()
        print(f"Finished reading chunk of {num_points} data points from file {file}")
        #delete the original file
        if "+" in file:
            os.remove(file)


        #data_chunk = lines.T.astype(float)
    #f.close()
    #with open(file, 'w') as f:
    #    f.writelines(lines)

    #fp.close()
    #data_chunk = data_chunk.astype(float)


    #with open(file, 'rb') as f:
    #    f.seek(start_idx * num_ch * 4)  # 4 Bytes for int32
    #    data_chunk = np.fromfile(f, dtype=np.int32, count=num_points * num_ch).reshape(-1, num_ch).T
    #f.close()
    #dc = copy(data_chunk)
    #del data_chunk
    #del db
    gc.collect()
    return data_chunk"""
        
def load_bin_data_chunked(file_arr, start_idx, num_points, num_ch, file_len):

    data_chunk = np.full((num_ch, num_points),np.nan, dtype=float)
    #with open(file, 'r') as f:
        #lines = 
    #for i, line in tqdm(enumerate(f.readlines()), total=num_points):
    i = -1
    #search for +'s in dir, and load the one with the highest number

    print(f"Reading chunk of {num_points} data points from file starting at index {start_idx}")
    data_chunk = file_arr[start_idx:start_idx+num_points].T

    gc.collect()
    return data_chunk

"""def apply_conversion_factors(data_all, num_ch, mag_data):
    for i in range(num_ch):
        ch = i + 1
        data_all[i] *= 0.0001331253868#!make sure this is correct
        if mag_data:
            # if ch % 2 == 0:  # Mag612 are at even channels and Mag690 at odd
            #     data_all[i] *= (90 / 8)
            if ch in [7,9,11,13,15,17]:
                data_all[i] *= (70 / 10)  # Mag03 in µT
            else:
                data_all[i] *= (100 / 10)  # Mag690 in µT
    return data_all"""

"""@np.vectorize
def apply_conversion_factors(data_all, num_ch, mag_data):
    #ch = i + 1
    odd_channels = np.array([6,8,10,12,14,16])
    data_all *= 0.0001331253868#!make sure this is correct
    if mag_data:
        # if ch % 2 == 0:  # Mag612 are at even channels and Mag690 at odd
        #     data_all[i] *= (90 / 8)
        data_all[odd_channels] *= (70 / 10)  # Mag03 in µT
        data_all[~odd_channels] *= (100 / 10)  # Mag690 in µT
    return data_all"""

#truncate to channels
#odd_channel_mask = odd_channel_mask[:num_ch]#!temp
#@np.vectorize
def apply_conversion_factors(data_all : np.ndarray) -> np.ndarray:
    data_all = data_all * conversion_factor 
    data_all = data_all*1e-9#!nanoTesla
    return data_all


def load_and_downsample_files(filelist, freq, target_fs, num_ch, max_memory_usage_mb):
    down_factor = int(freq / target_fs)
    dtype = np.float32
    chunk_size = int((max_memory_usage_mb * (1024 ** 2)))  # in data points per channel
    #prev_chunk_end = None
    collected_chunk = None
    starting_chunk_len = chunk_size//4*down_factor//num_ch
    target_chunk_len = chunk_size//4//num_ch
    data_2write = []
    print(f"Collecting into chunks of len: {starting_chunk_len}")
    print(f"And downsamling to len: {target_chunk_len}")
    #todo:
    #replace all_data by file-system solution
    #all_data = []
    #os.makedirs("temp_alldata", exist_ok=True)
    #new file
    for f in os.listdir(path):
        if "all_data_block" in f:
            os.remove(f"{path}{f}")
    """with open("temp_alldata/dat.txt", "w") as f:
        f.write("")
    f.close()"""
    def get_blockindex():
        block_index = len(os.listdir(path))+1
        return block_index
    block = 0
    chunk = 0
    #filelist = [f for f in filelist if "+" not in f]
    assert len(filelist) > 0, "No files found"
    for file in filelist:
        #all_data = []
        print(f"Data is loaded from file {file}")
        #print("done")
        file_shape_meta = file.replace(".npy", "_shape.txt")
        if os.path.exists(file_shape_meta):
            shape = open(file_shape_meta, "r").read()
            shape = eval(shape)
        #file_arr = np.memmap(file, dtype=np.float32, mode='r', shape=shape)
        file_arr = np.load(file, mmap_mode='r')
        file_arr = file_arr[1:]
        #plt plot as a tes
        """plt.plot(file_arr[:100000000,0])
        plt.savefig(f"{path}testplot.png")
        plt.close()"""
        total_points = file_arr.shape[0]
        print(f"Total points: {total_points}")
        print(f"Size of array: {file_arr.nbytes / (1024 ** 2)} MB")

        #append to collected chunk
        #collected_chunk = np.append(collected_chunk, file_arr, axis=0)
        if collected_chunk is None:
            collected_chunk = file_arr
        else:
            raise NotImplementedError("Have still not vallidated wether it keeps the memmap")#!validate
            collected_chunk = np.concatenate((collected_chunk, file_arr), axis=0)
        print(f"Collected chunk has shape {collected_chunk.shape}")
        while collected_chunk.shape[0] >= starting_chunk_len:
            print(f"Chunk is larger than {starting_chunk_len}, downsampling")
            down_sample_chunk = collected_chunk[:starting_chunk_len]
            sampled_chunk = resample(down_sample_chunk, target_chunk_len, axis=0)
            sampled_chunk = apply_conversion_factors(sampled_chunk.T)
            np.save(f"{path}{name}all_data_block_{get_blockindex()}.npy", sampled_chunk)
            del collected_chunk[:starting_chunk_len]
            del sampled_chunk
            del down_sample_chunk
            gc.collect()
            print(f"Chunk has been downsampled and saved")
    while collected_chunk.shape[0] > 0:
        print(f"Chunk is larger than {starting_chunk_len}, downsampling")
        down_sample_chunk = collected_chunk[:starting_chunk_len]
        sampled_chunk = resample(down_sample_chunk, target_chunk_len, axis=0)
        sampled_chunk = apply_conversion_factors(sampled_chunk)
        np.save(f"{path}{name}all_data_block_{get_blockindex()}.npy", sampled_chunk.T)
        collected_chunk = collected_chunk[starting_chunk_len:]
        del sampled_chunk
        del down_sample_chunk
        gc.collect()
        print(f"Chunk has been downsampled and saved")



    """    for start_idx in range(0, total_points, chunk_size):
            num_points = min(chunk_size, total_points - start_idx)
            data_chunk = load_bin_data_chunked(file_arr, start_idx, num_points, num_ch, total_points+1)#!possible read trouble?
            print(f"Datachunk with shape {data_chunk.shape} loaded")
            if data_chunk.shape[1] < file_arr.shape[0]/down_factor:
                print(f"Data chunk is smaller than expected: {data_chunk.shape[1]} vs {file_arr.shape[0]}")
                prev_chunk_end = data_chunk
                raise ValueError("Data chunk is smaller than expected")
            #data_chunk = apply_conversion_factors(data_chunk, num_ch, mag_data)
            print("Applying conversion factors")
            data_chunk = apply_conversion_factors(data_chunk)#!possible conversion trouble?
            print("done")
            #now it is a (num_ch, num_points) array

            # Combine with previous chunk if necessary
            if prev_chunk_end is not None:
                data_chunk = np.concatenate((prev_chunk_end, data_chunk), axis=1)#!just make sure this is correct

            

            # Calculate the number of complete sections to downsample
            num_complete_sections = data_chunk.shape[1] // down_factor * down_factor

            if data_chunk[:, :num_complete_sections].shape[1] >= down_factor:#! i like this (although I do think it truncates the last chunk)
                downsampled_chunk = downsample_data(data_chunk[:, :num_complete_sections], freq, target_fs)#!doublecheck this downsamlper
                all_data.append(downsampled_chunk)
                print(f"Chunk {chunk} downsampled")
                chunk+=1
                lenalldata = np.concatenate(all_data, axis=1).flatten().size
                blocksize = np.concatenate(all_data, axis=1).nbytes / (1024 ** 2)
                print(f"Data points in current block: {lenalldata} (about {round(blocksize,2)} MB) as compared to {block_size_mb} MB")
                # Save the block if it reaches the defined size
                if  blocksize >= block_size_mb:
                    final_data = np.concatenate(all_data, axis=1)
                    
                    np.save(f"{path}{name}all_data_block_{block_index}.npy", final_data)

                    
                    print(f"Block {block} saved to file")
                    #all_data = []  # Clear the list to free memory
                    block+=1
                    del all_data
                    gc.collect()
                    all_data = []
            # Save the remaining data points for the next chunk
            prev_chunk_end = data_chunk[:, num_complete_sections:]

            # Free memory
            del data_chunk
            gc.collect()
        print(f"Finished processing file {file}")

            
    # Process any remaining data at the end of the last file
    if prev_chunk_end is not None and prev_chunk_end.shape[1] > 0:
        if prev_chunk_end.shape[1] >= down_factor:
            downsampled_chunk = downsample_data(prev_chunk_end, freq, target_fs)
            all_data.append(downsampled_chunk)
    if all_data:
        final_data = np.concatenate(all_data, axis=1)
        block_index = len(os.listdir(path))
        np.save(f"{path}{name}all_data_block_{block_index}.npy", final_data)
        print("Final Block Saved")
        del final_data
    #clean up
    del all_data
    del prev_chunk_end
    del downsampled_chunk
    gc.collect()"""



def downsample_data(data, original_fs, target_fs):
    down_factor = int(original_fs / target_fs)
    return decimate(data, down_factor, axis=1, zero_phase=True)



def load_all_downsampled_data(path):
    files = natsorted([f for f in os.listdir(path) if f.endswith('.npy')])
    all_data = [np.load(os.path.join(path, file)) for file in files]
    return np.concatenate(all_data, axis=1)

def plot_all_channels(data, num_ch):
    import matplotlib.pyplot as plt
    plt.rcParams['agg.path.chunksize'] = 100000000
    cmap = plt.get_cmap('plasma')
    cmaplist = [cmap(x) for x in np.linspace(0,0.82,num=18)]

    time = np.linspace(0, data.shape[1] / target_fs, num=data.shape[1])
    plt.figure(figsize=(10, 8))
    for i in range(num_ch):
        plt.scatter(time, data[i])# color = cmaplist[i], label=f'Channel {i+1}')
    plt.xlabel('Time [s]')
    plt.ylabel('Signal')
    plt.title('All Channels vs Time')
    plt.legend(loc='upper right')
    plt.savefig(f"{path}All_channels_vs_time.png")
    plt.show()

def directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory '{path}' was created.")
    else:
        print(f"Directory '{path}' already exists.")

def create_readme(path, content=None):
    readme_content = ""
    if content:
        readme_content += f"\n## \n{content}\n"
    with open(f"{path}README.txt", "a") as readme_file:
        readme_file.write(readme_content)

def run_main():
    gc.collect()
    directory(path)
    list_of_files = find_files(data_path)
    
    load_and_downsample_files(list_of_files, freq, target_fs, num_ch, max_memory_usage_mb)
    
    #part 2

    if mag_data:
        dataconversion = "Data was converted to muT"
    else:
        dataconversion = "data is still in V"
    
    create_readme(path, content=f"Data from {data_path} with {num_ch} channels and an original frequency of {freq} Hz taken and downsampled to {target_fs}Hz. Saved to npy file in {path}. {dataconversion}.")
    
    gc.collect()
    combined_data = load_all_downsampled_data(path)
    plot_all_channels(combined_data, num_ch)
    
    print("\nFinished\n")

if __name__ == '__main__':
    run_main()

