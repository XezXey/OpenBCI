# Import using libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import Filters
import datetime


class PreprocessingAndAggregateOpenBCI:
    
    def __init__(self, filename, filemode=1, process_channel=['Channel 1', 'Channel 2']):
        self.filename = filename
        self.filemode = filemode
        self.process_channel = process_channel
        self.ecg_data = pd.read_csv(self.filename, usecols=['Time', 'Timestamp'] + self.process_channel)
        self.possible_start_time = None
        self.possible_end_time = None
        self.estimated_heart_rate_by_time_ibi_and_count_heart_rate_by_time = pd.DataFrame()
        self.ecg_feature_df_interest_interval = None
        self.aggregate_interest_interval = None
        self.time_interval = None
        self.ecg_feature_df_interest_interval_sep_channel = []

    
    def get_time_interval(self):
        # Get the possible time interval in data for ensure that your interest interval is able to reach
        self.possible_start_time = self.ecg_data.loc[0, 'clock']
        self.possible_end_time = self.ecg_data.loc[len(self.ecg_data)-1, 'clock']
        print("Possible time interval [" + str(self.possible_start_time) + ',' + str(self.possible_end_time) + ']')
        
    
    def filter_function(self):
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
        
    # Iterate in every channel to process
        for i in range(0, len(self.process_channel)):
            print(self.process_channel[i] + " Processing...")
            # 1. Power supply filter(50 Hz) : Apply Notch filter to signal
            print("Apply notch filter...", end='')
            filter_signal = Filters.Filters(window_size=10, low=0.67, high=5)
            ecg_data_notched_50 = filter_signal.notch_filter(self.ecg_data[self.process_channel[i]], hz='50')
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
            
            self.ecg_data[self.process_channel[i] + '_filtered'] = ecg_finale_data
            
            # 5. Visualization
            # frequency is 250Hz
            # number_of_data = 250 * x (seconds)
            
            print("Visualization...")
            # 1. Plotting raw data
            plt.figure()
            plt.plot(self.ecg_data[self.process_channel[i]][2500:5000])
            plt.title('ECG Raw data : ' + self.process_channel[i])
            plt.xlabel('Time(s)')
            plt.ylabel('Amplitude(uV)')
            
            
            # 2. Plotting data after apply 50Hz notch filter
            plt.figure()
            plt.plot(ecg_data_notched_50[2500:5000])
            plt.title('ECG with Notched filter(50 Hz) : ' + self.process_channel[i])
            plt.xlabel('Time(s)')
            plt.ylabel('Amplitude(uV)')
            
            # 3. Plotting data after apply breathing filter(0.5 Hz)
            plt.figure()
            plt.plot(ecg_data_breathing[2500:5000])
            plt.title('ECG with Breathing filter(0.5 Hz) : ' + self.process_channel[i])
            plt.xlabel('Time(s)')
            plt.ylabel('Amplitude(uV)')
            
            # 4. Plotting data after apply R-peak filter(15-20 Hz)
            plt.figure()
            plt.plot(ecg_data_r_peak[2500:5000])
            plt.title('ECG with R-Peak filter(15-20 Hz) : ' + self.process_channel[i])
            plt.xlabel('Time(s)')
            plt.ylabel('Amplitude(uV)')
            
            # 5. Plotting data after apply ECG range filter(0.67-5 Hz)
            plt.figure()
            plt.plot(ecg_finale_data[2500:4000])
            plt.title('ECG with applied ECG range filter : ' + self.process_channel[i])
            plt.xlabel('Time(s)')
            plt.ylabel('Amplitude(uV)')
    
            print('All Done!')
        return self.ecg_data
    
    
    
    
    def extract_hr_rr(self):
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
        
        for i in range(0, len(self.process_channel)):
            print(self.process_channel[i] + " : Finding Peak-R and R-R Interval...", end='')
            # 1.Find peak in each channel
            peaks, _ = find_peaks(self.ecg_data[self.process_channel[i] + '_filtered'], distance=150)
            
            # 2. Find rr_interval between each peak
            rr_interval = 250 / np.diff(peaks)
            
            # Store each rr_interval into the dataframe
            self.ecg_data.loc[peaks[0:-1], self.process_channel[i] + '_rr_interval'] = rr_interval
            
            # Store each estimated_heart_rate_from_rr into dataframe
            self.ecg_data.loc[peaks[0:-1], self.process_channel[i] + '_estimated_heart_rate_from_rr'] = 60/rr_interval
            
            print('Done!')
    
        return self.ecg_data
    
    
    def get_estimated_heart_rate_ibi_and_count_heart_rate_by_time(self):
        ############################################################################################
        # get_estimated_heart_rate_ibi_and_count_heart_rate
        # 1. Estimated heart rate calculate
        #   1.1 Grouping clock at the same time
        #   1.2 Finding the average of estiamted heart rate in the same interval(in 1 minutes)
        # 2. IBI
        #   2.1 Grouping clock at the same time
        #   2.2 IBI = rr_interval
        # 3. Count heart rate
        #   3.1 Grouping clock at the same time
        #   3.2 Count number of rr_interval that happen in every 1 seconds ===> this mean we have
        #       the number of heart beat in each seconds
        #
        #   Input : ecg_data(Dataframe type)
        #   Output : Dataframe of estimated heart rate, IBI and count heart rate sort by time
        #
        #
        ###########################################################################################
        
        if self.filemode == 0:  # Data came from "GUI" => There's only Timestamp columns provided
                self.ecg_data['Timestamp'] = self.ecg_data['Timestamp']/1000    # Divide by 1000 to take the milliseconds out
                self.ecg_data['date'] = self.ecg_data['Timestamp'].apply(lambda x : datetime.datetime.fromtimestamp(x).date())   # Apply datetime.datetime.fromtimestamp to extract date and clock
                self.ecg_data['clock'] = self.ecg_data['Timestamp'].apply(lambda x : datetime.datetime.fromtimestamp(x).time())
                
        elif self.filemode == 1: # Data came from "Python script" => There's Time columns provided
                
                ###### In the future, If I need to process in microseconds I use to add %f in time pattern like this "%Y-%m-%d_%H-%M-%S-%f"
                self.ecg_data['date'] = self.ecg_data['Time'].apply(lambda each_time : datetime.datetime.strptime(each_time, "%Y-%m-%d_%H-%M-%S").date())
                self.ecg_data['clock'] = self.ecg_data['Time'].apply(lambda each_time : datetime.datetime.strptime(each_time, "%Y-%m-%d_%H-%M-%S").time())
                
        for i in range(0, len(self.process_channel)):
            self.estimated_heart_rate_by_time_ibi_and_count_heart_rate_by_time[self.process_channel[i] + '_estimated_heart_rate_by_time'] = self.ecg_data.groupby(self.ecg_data['clock'])[self.process_channel[i] + '_estimated_heart_rate_from_rr'].mean()
            self.estimated_heart_rate_by_time_ibi_and_count_heart_rate_by_time[self.process_channel[i] + '_rr_interval(IBI)'] = self.ecg_data.groupby(self.ecg_data['clock'])[self.process_channel[i] + '_rr_interval'].mean()
            self.estimated_heart_rate_by_time_ibi_and_count_heart_rate_by_time[self.process_channel[i] + '_count_heart_rate'] = self.ecg_data.groupby('clock')[self.process_channel[i] + '_rr_interval'].apply(lambda x: x[x != np.nan].count())
    
        return self.estimated_heart_rate_by_time_ibi_and_count_heart_rate_by_time
    
    
    def get_interest_interval_information(self, ecg_feature_df, start_time, end_time):
        #######################################################################################################################
        # get_interest_interval_information
        # 1. Aggregate the information between start_time to end_time interval
        #   1.1 Slice the dataframe using start_time and end_time by a minute
        #   1.2 Aggregate the data using Mean, Sum and Std
        #
        # 2. Calculate time interval from start_time to end_time
        #   2.1 Convert the datetime.datetime object into datetime.timedelta object that can apply the minus operation to find
        #       the difference of time
        #
        #
        #   Input : 1.ecg_feature_df(Dataframe after extract important features and ready to summarize or slice),
        #           2. start_time and end_time of interest time interval
        #   Output : 1. ecg_feature_df_interest_interval that already sliced the data
        #            2. aggregate_interest_interval that already aggregate the data (Mean, Max and Std)
        #            3. time_interval between start_time to end_time
        #
        #######################################################################################################################
        
        
        
        # Define start_time and end_time object to compute the interval range
        start_time_object = datetime.datetime.strptime(start_time, '%H:%M:%S')
        end_time_object = datetime.datetime.strptime(end_time, '%H:%M:%S')
        
        # Parse datetime.datetime object into datetime.timedelta object for apply minus signs
        start_time_timedelta = datetime.timedelta(hours=start_time_object.hour, minutes=start_time_object.minute, 
                                                  seconds=start_time_object.second, microseconds=start_time_object.microsecond)
        end_time_timedelta = datetime.timedelta(hours=end_time_object.hour, minutes=end_time_object.minute, 
                                                seconds=end_time_object.second, microseconds=end_time_object.microsecond)
        
        self.time_interval = end_time_timedelta - start_time_timedelta
        
        self.ecg_feature_df_interest_interval = ecg_feature_df.loc[start_time_object.time():end_time_object.time()]
        
        self.aggregate_interest_interval = pd.DataFrame(self.ecg_feature_df_interest_interval.sum(), columns=['Sum'])
        self.aggregate_interest_interval = pd.DataFrame(self.ecg_feature_df_interest_interval.mean(), columns=['Mean'])
        self.aggregate_interest_interval = pd.DataFrame(self.ecg_feature_df_interest_interval.std(), columns=['Std'])
    
    
            
        return self.ecg_feature_df_interest_interval, self.aggregate_interest_interval, self.time_interval
    

    def get_feature_df_interest_interval_each_channel(self):
        self.ecg_feature_df_interest_interval_each_channel = []
        for i in range(0, len(self.process_channel)):
            temp = self.ecg_feature_df_interest_interval[[self.process_channel[i] + '_estimated_heart_rate_by_time', self.process_channel[i] + '_rr_interval(IBI)', 
                                                   self.process_channel[i] + '_count_heart_rate']].dropna()
            self.ecg_feature_df_interest_interval_sep_channel.append(temp)
        return self.ecg_feature_df_interest_interval_sep_channel

"""
Code for testing
#Main program class
filename = '../reformed/ex1_OpenBCI-RAW-2561-11-16_21-53-48_reform.csv'
file_mode = 0   # 0 = GUI and Python script(has only timestamp), 1 = Python script ===> This will affect to extract date and clock from timestamp
process_channel=['Channel 1', 'Channel 2']
preprocessing_and_aggregate_data = PreprocessingAndAggregateOpenBCI(filename, file_mode, process_channel)
ecg_data_filtered = preprocessing_and_aggregate_data.filter_function()
ecg_data_hr_rr = preprocessing_and_aggregate_data.extract_hr_rr()
ecg_data_estimated = preprocessing_and_aggregate_data.get_estimated_heart_rate_ibi_and_count_heart_rate_by_time()

# Get the possible time interval in data for ensure that your interest interval is able to reach
preprocessing_and_aggregate_data.get_time_interval()

# Get data and aggregate information only in interest time interval
# Define start_time and end_time of interest time interval
start_time = '21:54:30'
end_time = '22:10:37'
ecg_feature_df_interest_interval, aggregate_interest_interval, time_interval = preprocessing_and_aggregate_data.get_interest_interval_information(ecg_data_estimated, start_time, end_time)

ecg_feature_df_interest_interval_sep_channel = preprocessing_and_aggregate_data.get_feature_df_interest_interval_each_channel()

"""
"""
# Main program script
# Import Raw signal to apply filter later
print("Loading data...", end='')
filename = '../reformed/ex1.csv_2018-11-16_22-18-48_reform.csv'
file_mode = 1   # 0 = GUI and Python script(has only timestamp), 1 = Python script ===> This will affect to extract date and clock from timestamp
ecg_data = pd.read_csv(filename)
print("Done!")

# Define process_channel to locate which channel to process
process_channel = ['Channel 1']

# Select time columns to process
# If data came from GUI => better to use timestamp columns
ecg_data = ecg_data[['Time', 'Timestamp'] + process_channel]

# Pass ecg_data dataframe to filter out the noise and the supply offset
ecg_data = filter_function(ecg_data, process_channel)

# Pass ecg_data to find Peak-R, RR Interval and heart rate
ecg_data = extract_hr_rr(ecg_data, process_channel)


# Get get_estimated_heart_rate_ibi_and_count_heart_rate from preprocessing data
# This is final data and can be use to compare with empatica data
ecg_feature_df = get_estimated_heart_rate_ibi_and_count_heart_rate(ecg_data, process_channel, file_mode)

# Get the possible time interval in data for ensure that your interest interval is able to reach
possible_start_time = ecg_data.loc[0, 'clock']
possible_end_time = ecg_data.loc[len(ecg_data)-1, 'clock']
print("Possible time interval [" + str(possible_start_time) + ',' + str(possible_end_time) + ']')

# Get data and aggregate information only in interest time interval
# Define start_time and end_time of interest time interval
start_time = '10:02:15'
end_time = '10:16:55'
# Pass interval_time and ecg_feature_df to get the data and aggregate in interest time interval
ecg_feature_df_interest_interval, aggregate_interest_interval, time_interval = get_interest_interval_information(ecg_feature_df, start_time, end_time)
non_nan_ecg_feature_df_interest_interval = ecg_feature_df_interest_interval.dropna()    # Drop Nan becayse time is in milliseconds unit ===> There's no R-Peak in that milliseconds = Lots of Nan
print("Interesting time interval [" + start_time + ',' + end_time + '] : ' + str(time_interval))
"""
