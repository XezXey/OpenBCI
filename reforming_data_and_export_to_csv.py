#Import some useful libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import fnmatch
###########################################################################
#	 	                 OpenBCI data pattern	                          #
#1. Received data from GUI platform                                       #
#  -Data pattern : ['Index', 'Channel 1', 'Channel 2', 'Channel 3',       #
#      'Channel 4', 'Channel 5', 'Channel 6', 'Channel 7', 'Channel 8',   # 
#      'Channel 9(AX)', 'Channel 10(AY)', 'Channel 11(AZ)', 'Time',       #
#      'Timestamp']                                                       #
#                                                                         #
#2. Received data from python script (inlude time)                        #
#  -Data pattern : ['Timestamp', 'Index', 'Channel 1', 'Channel 2',       #
#        'Channel 3', 'Channel 4', 'Channel 5', 'Channel 6','Channel 7',  #
#        'Channel 8', 'Channel 9(AX)', 'Channel 10(AY)', 'Channel 11(AZ)' #
#        ,'Time']                                                         #
#  ****This pattern work with OpenBCI_Python(edit by me)                  #
#                                                                         #
#3. Received data from python script (not inlucde time)                   #
#  -Data pattern : ['Timestamp', 'Index', 'Channel 1', 'Channel 2',       #
#        'Channel 3', 'Channel 4', 'Channel 5', 'Channel 6','Channel 7',  #
#        'Channel 8', 'Channel 9(AX)', 'Channel 10(AY)', 'Channel 11(AZ)' #
#  ****This pattern is original version of OpenBCI_Python                 #
###########################################################################

###########################################################################
#                     How to use this script                              #
#1. Input filename as a parameters                                        #
#2. Select data pattern that you want                                     #
#3. Drink some coffee                                                     #  
###########################################################################

#Prepare folder to contain every reformed files
outdir = './reformed'
if not os.path.exists(outdir):
    os.mkdir(outdir)

#Loading all input file from argv to process_file list.
process_file = []    #Store all filename
for filename in os.listdir('./unreform'):
    if fnmatch.fnmatch(filename, sys.argv[1]):
        if filename[-11:-4] != "_reform":
            process_file.append(filename)


if len(process_file) > 0:    
    print("File need to process : ", end='')
    print(process_file)
else:
    print("No input file")

#Define number of rows to skip
n_skip_rows = [6, 1, 1]    #7 rows for GUI csv file pattern, 1 rows for python file pattern
#Define csv file pattern from
#From OpenBCI_GUI
col_names_GUI = ['Index', 'Channel 1', 'Channel 2', 'Channel 3', 'Channel 4', 'Channel 5', 'Channel 6',
             'Channel 7', 'Channel 8', 'Channel 9(AX)', 'Channel 10(AY)', 'Channel 11(AZ)', 'Time', 'Timestamp']

#From OpenBCI_Python script 
col_names_py_no_time = ['Timestamp', 'Index', 'Channel 1', 'Channel 2', 'Channel 3', 'Channel 4', 'Channel 5', 'Channel 6',
             'Channel 7', 'Channel 8', 'Channel 9(AX)', 'Channel 10(AY)', 'Channel 11(AZ)']

#From OpenBCI_Python script 
col_names_py_add_time = ['Timestamp', 'Index', 'Channel 1', 'Channel 2', 'Channel 3', 'Channel 4', 'Channel 5', 'Channel 6',
             'Channel 7', 'Channel 8', 'Channel 9(AX)', 'Channel 10(AY)', 'Channel 11(AZ)', 'Time']


col_name_choice = [col_names_GUI, col_names_py_no_time, col_names_py_add_time]

#Forming data into compatible form
compat_col = ['Timestamp', 'Channel 1', 'Channel 2', 'Channel 3', 'Channel 4', 'Channel 5', 'Channel 6',
             'Channel 7', 'Channel 8', 'Channel 9(AX)', 'Channel 10(AY)', 'Channel 11(AZ)']

#Processing each input file
for filename in process_file:
    print("\nProcessing : " + filename)
    source_choice = int(input("Select your file platform(0=OpenBCI_GUI, 1=OpenBCI_Python_no_time, 2=OpenBCI_Python_add_time) : " ))
    ecg_file = pd.read_csv('./unreform/' + filename, skiprows=n_skip_rows[source_choice], sep=',', header=None, names=col_name_choice[source_choice])
    print(ecg_file.head(3))
    print(ecg_file.columns)
    ecg_file = ecg_file.dropna()
    ecg_file_reformed = ecg_file[compat_col]
    ecg_file_reformed.to_csv("./reformed/" + filename[:-4] + "_reform.csv", index=False)
    print("\n")
print("End...........")
