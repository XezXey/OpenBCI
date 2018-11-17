# Import using libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import Filters

#####################################################################################
# Filter process
# 1. Power supply filter(50 Hz) : Apply Notch filter to remove the power supply freq.
# 2. Breathing muscle filter(0.5 Hz) : Apply highpass filter.
# 3. R-Peak filtering(15-20Hz) : Apply bandpass filter
# 4. ECG range filter(0.67-5Hz) : Apply bandpass filter
#
#   Input : Dataframe
#   Output : Filtered signal
#
##################################################################################### 

def filter_function(ecg_data, process_channel):
# Iterate in every channel to process
    for i in range(0, len(process_channel)):
        print(process_channel[i] + " Processing...")
        # 1. Power supply filter(50 Hz) : Apply Notch filter to signal
        print("Apply notch filter...", end='')
        filter_signal = Filters.Filters(window_size=10, low=0.67, high=5)
        ecg_data_notched_50 = filter_signal.notch_filter(ecg_data[process_channel[i]], hz='50')
        print("Done!")
        
        
        # 2. Breathing Muscle filter(0.5 Hz) : Apply highpass filter to get rid off breathing muscle signal
        # Instance the filter object and set the following parameter
        print("Apply breathing filter...", end='')
        breathing_filter = Filters.Filters(window_size=10, low=0.5, high=5)
        ecg_data_breathing = breathing_filter.high_pass(ecg_data_notched_50)
        print("Done!")
        
        
        # 3. R-Peak filter : Apply 15-20 Hz bandpass filter
        # High pass with 15 Hz and Low pass with 20 Hz
        print("Apply R-peaks filter...", end='')
        r_peak_filter = Filters.Filters(window_size=10, low=15, high=20)
        ecg_data_r_peak = r_peak_filter.high_pass(ecg_data_breathing)
        ecg_data_r_peak = r_peak_filter.low_pass(ecg_data_r_peak)
        print("Done!")
        
        # 4. ECG range filter (0.67-5Hz)
        print("Apply bandpass filter(0.67-5Hz)...", end='')
        ecg_finale_data = filter_signal.bandpass(ecg_data_r_peak)
        print("Done!")
        
        ecg_data[process_channel[i] + '_filtered'] = ecg_finale_data
        
        # 5. Visualization
        # frequency is 250Hz
        # number_of_data = 250 * x (seconds)
        
        print("Visualization...")
        # 1. Plotting raw data
        plt.figure()
        plt.plot(ecg_data[process_channel[i]][2500:5000])
        plt.title('ECG Raw data : ' + process_channel[i])
        plt.xlabel('Time(s)')
        plt.ylabel('Amplitude(uV)')
        
        
        # 2. Plotting data after apply 50Hz notch filter
        plt.figure()
        plt.plot(ecg_data_notched_50[2500:5000])
        plt.title('ECG with Notched filter(50 Hz) : ' + process_channel[i])
        plt.xlabel('Time(s)')
        plt.ylabel('Amplitude(uV)')
        
        # 3. Plotting data after apply breathing filter(0.5 Hz)
        plt.figure()
        plt.plot(ecg_data_breathing[2500:5000])
        plt.title('ECG with Breathing filter(0.5 Hz) : ' + process_channel[i])
        plt.xlabel('Time(s)')
        plt.ylabel('Amplitude(uV)')
        
        # 4. Plotting data after apply R-peak filter(15-20 Hz)
        plt.figure()
        plt.plot(ecg_data_r_peak[2500:5000])
        plt.title('ECG with R-Peak filter(15-20 Hz) : ' + process_channel[i])
        plt.xlabel('Time(s)')
        plt.ylabel('Amplitude(uV)')
        
        # 5. Plotting data after apply ECG range filter(0.67-5 Hz)
        plt.figure()
        plt.plot(ecg_finale_data[2500:4000])
        plt.title('ECG with applied ECG range filter : ' + process_channel[i])
        plt.xlabel('Time(s)')
        plt.ylabel('Amplitude(uV)')

        print('All Done!')
    return ecg_data




def extract_hr_rr(ecg_data, process_channel):
    ############################################################################################
    # Extract Heart rate and R-R Interval
    # 1. R-R Interval
    #   1.1 Use find_peaks function to find the "Peak-R" position
    #   1.2 Store R position into dataframe as "peak_pos" column [peak_value or 0=this isn't peak]
    #   1.3 Use np.diff to calculate the interval range between each Peak-R
    #   1.4 Store R-R Interval into dataframe as "rr_interval" column
    #
    # 2. Heart rate
    #   2.1 Calculate estimated_heart_rate from given rr_interval using this equation 
    #                   estimated_heart_rate = 60(seconds) / (rr_interval)
    #   2.2 Calculate heart_rate in every 1 minute using index to count up to 250 values(250 Hz)       
    #
    #   Input : ecg_data(Dataframe type)
    #   Output : ecg_data including : [peak_r, peak_pos, heart_rate, estimated_heart_rate]
    #
    ############################################################################################
    
    for i in range(0, len(process_channel)):
        print(process_channel[i] + " : Finding Peak-R and R-R Interval...", end='')
        # 1.Find peak in each channel
        peaks, _ = find_peaks(ecg_data[process_channel[i] + '_filtered'], distance=150)
        
        # 2. Find rr_interval between each peak
        rr_interval = 250 / np.diff(peaks)
        
        # Store each rr_interval into the dataframe
        ecg_data.loc[peaks[0:-1], process_channel[i] + '_rr_interval'] = rr_interval
        
        # Store each estimated_heart_rate_from_rr into dataframe
        ecg_data.loc[peaks[0:-1], process_channel[i] + '_estimated_heart_rate_from_rr'] = 60/rr_interval
        

    ecg_data = ecg_data.fillna(0)
    return ecg_data




# Main program
# Import Raw signal to apply filter later
print("Loading data...", end='')
ecg_data = pd.read_csv('../reformed/ex1.csv_2018-11-16_22-18-48_reform.csv')
print("Done!")
process_channel = ['Channel 1', 'Channel 2']
ecg_data = ecg_data[['Time', 'Timestamp', 'Channel 1', 'Channel 2']]
ecg_data = filter_function(ecg_data, process_channel)
ecg_data = extract_hr_rr(ecg_data, process_channel)

ecg_data['Timestamp'] = np.floor(ecg_data['Timestamp'])
ecg_data.groupby(ecg_data['Timestamp']).a(ecg_data['estimated_heart_rate_from_rr'])

