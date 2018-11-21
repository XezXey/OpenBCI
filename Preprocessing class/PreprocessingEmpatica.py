import pandas as pd
import numpy as np
import datetime

class PreprocessingEmpatica:
    ################################################################################################################################################
    # PreprocessingEmpatica class
    # 1. Adding timestamp and preprocess data both from hr.csv and ibi.csv
    # 2. and 3. Get time list for heart rate because hr.csv only provide the start of collcecting data time. So we need to add time to column
    # 4. Get time interval for let user know what's possible time range to interest in the data
    # 5. Get dataframe for both hr and ibi data by slicing into interest interval
    #
    ################################################################################################################################################
    
    
    def __init__(self, filename_hr, filename_ibi):
        # Initialization of attribute 
        self.filename_hr = filename_hr    # Contain filename of hr.csv to load
        self.filename_ibi = filename_ibi    # Contain filename of ibi.csv to load
        
        self.empatica_hr = pd.read_csv(self.filename_hr, names=['heart_rate'], header=None)    # Load hr.csv file into dataframe and names the column to 'heart_rate'
        self.empatica_ibi = pd.read_csv(self.filename_ibi, names=['peak_pos', 'rr_interval'], header=None)     # Load IBI.csv file into dataframe and names the column to 'peak_pos' and 'rr_interval'
       
    def get_hr_time_list(self, empatica_data_hr, utc_datetime):
        ####################################################################################################################################################
        # Getting time list for hr_data
        # 1. In hr.csv, Empatica did't provide every timestamp in each row. So this method will use the sampling rate of heart_rate data
        #       and increase the time from startpoint until the endpoint
        # *** This method called by add_timestamp_and_preprocess_hr_data
        #   Input : Raw data of empatica_hr, utc_datetime extracted from timestamp
        #   Output : ['Time'] column that contain the start time and increasing by 1/sampling rate (hr has 1 Hz sampling rate = 1 seconds per row increment)
        ####################################################################################################################################################
        
        time_list = []    # Contain time for each record extracted from timestamp
        # Iterate over empatica_data_hr to increase each time for each row using sampling rate and append into time_list variable
        for i in range(0, len(empatica_data_hr)): 
            utc_datetime += datetime.timedelta(seconds=1/self.sampling_rate_hr)
            time_list.append(utc_datetime)
        return time_list
    
    def add_timestamp_and_preprocess_hr_data(self):
        ###############################################################################################################################################################
        # Adding timestamp and preprocess(strip 2 first rows) for "Heart rate" data
        # 1. Compute the start time of data using datetime.datetime.fromtimestamp method in first row => this will get the start of time in GMT+7 (Current local time)
        # 2. Get sampling rate from the second row of dataframe
        # 3. Remove 2 first row and reset the index to make the first row is the first heart rate and start with index 0
        # 4. Call self.get_time_list method to get series of time for each row
        # 5. Extract the ['date'] column and ['clock'] column from each timestamp in each row
        # 6. Set Index using ['clock'] column
        #
        #   Input : Attributes name empatica_hr, sampling_rate_hr and utc_datetime_hr
        #   Output : Preprocessed the empatica_hr dataframe
        ###############################################################################################################################################################
    
        utc_datetime_hr = datetime.datetime.fromtimestamp(self.empatica_hr['heart_rate'][0])    # get current local time from timestamp(first row of data)
        self.sampling_rate_hr = self.empatica_hr['heart_rate'][1]    # Get sampling rate from second line of HR.csv files
        self.empatica_hr = self.empatica_hr.loc[2:, :]    #Cut 2 first row
        self.empatica_hr = self.empatica_hr.reset_index(drop=True)    # Reset index to make first row is index 0
        time_list = self.get_hr_time_list(self.empatica_hr, utc_datetime_hr)    # Get time_list from get_time_list method 
        
        self.empatica_hr['Timestamp'] = time_list    # Apply every time_list into ['Timestamp'] column
        self.empatica_hr['date'] = self.empatica_hr['Timestamp'].apply(lambda each_time : each_time.date())    # Extract ['date'] from ['Timestamp']
        self.empatica_hr['clock'] = self.empatica_hr['Timestamp'].apply(lambda each_time : each_time.time())    # Extract ['clock'] from ['Timestamp']
        self.empatica_hr = self.empatica_hr.set_index(self.empatica_hr['clock'])    # Set index from 0 to len(empatica_hr) into ['clock']
        
    def add_timestamp_and_preprocess_ibi_data(self):
        #######################################################################################################################################################################
        # Adding timestamp and preprocess(strip first rows) for "IBI" data
        # 1. Compute the start time of data using datetime.datetime.fromtimestamp method in first row => this will get the start of time in GMT+7 (Current local time)
        # 2. Remove first row and reset index start with 0
        # *** Data Description : the first column is time that detect the Peak-R, so using this column plus with start time will get the time that detect the Peak-R
        # ***    the second column is rr_interval between the current Peak-R and previous R
        # 3. Insert value 0 for use this add up with the start time (because np.diff isn't include the diff of first value so this will add time of first row by using diff)
        # 4. Extract the ['date'] column and ['clock'] column from each timestamp in each row
        # 5. Remove the microsecond part from ['clock'] column (but not update this column) and use this as index of dataframe (Easy to join and grouping with other dataframe)
        #
        #   Input : Attributes name empatica_ibi, utc_datetime_hr
        #   Output : Preprocessed the empatica_ibi dataframe
        ################################################################################################################################################################################################
        
        utc_datetime_ibi = datetime.datetime.fromtimestamp(self.empatica_ibi['peak_pos'][0])    # get current local time from timestamp(first row of data)
        self.empatica_ibi = self.empatica_ibi.loc[1:, :]    # Remove first row
        self.empatica_ibi = self.empatica_ibi.reset_index(drop=True)    # Reset index to make first row is index 0
        time_increment_from_initial = np.diff(self.empatica_ibi['peak_pos'])    # Find the time reference of each ['peak_pos'] by 
        time_increment_from_initial = np.insert(time_increment_from_initial, 0, 0)  # Insert value 0 into the first row for using this add with the start time
        time_list = []    # Contain time_list for each row
        # Iterate by len(time_increment_from_initial) and keep adding time from the initial with the difference of time between each 'peak_pos'
        # *** Diagram
        #   Initial(Get from timestamp) ===> t1(in timestamp) = Initial + peak_pos[1] - 0 ===> t2(in timestamp) = t1 + peak_pos[2] - peak_pos[1] ===> t3(in timestamp) = t2 + peak_pos[3] - peak_pos[2]
        #   All peak_pos provided in time_list calculated by np.diff
        for i in range(0, len(time_increment_from_initial)):
            utc_datetime_ibi += datetime.timedelta(seconds=time_increment_from_initial[i])
            time_list.append(utc_datetime_ibi)
        
        
        self.empatica_ibi['Timestamp'] = time_list    # Apply every time_list into ['Timestamp'] column
        self.empatica_ibi['date'] = self.empatica_ibi['Timestamp'].apply(lambda each_time : each_time.date())   # Extract ['date'] from ['Timestamp']
        self.empatica_ibi['clock'] = self.empatica_ibi['Timestamp'].apply(lambda each_time : each_time.time())    # Extract ['clock'] from ['Timestamp']
        
        #****************** Mention
        # Reset index from 0 - len(empatica_ibi) to ['clock']  and set the microseconds = 0 because @21/11/2018 version didn't use the microseconds in python script 
        # So if we didn't make it zero ===> It cannot use to join or grouping with other dataframe because of index is not the same
        self.empatica_ibi = self.empatica_ibi.set_index(self.empatica_ibi['clock'].apply(lambda each_time : each_time.replace(microsecond=0)))    

        
    def get_time_interval(self):
        #######################################################################################################################
        # Get the time interval
        # 1. Getting the possible time interval of empatica data 
        #   Input : Attributes name 'empatica_hr', 'empatica_ibi'
        #   Output : Dict of possible time interval of both ibi and hr data
        #######################################################################################################################
        
        return dict(empatica_hr_time_interval = str(self.empatica_hr.iloc[0]['clock']) + ' to ' + str(self.empatica_hr.iloc[-1]['clock']), empatica_ibi_time_interval = str(self.empatica_ibi.iloc[0]['clock']) + ' to ' + str(self.empatica_ibi.iloc[-1]['clock']))
        
    def get_df_interest_time_interval(self, start_time, end_time):
        #######################################################################################################################
        # Get the interest time interval by slicing the using start_time and end_time
        # 1. Slicing the dataframe into interest interval
        # *** Mention
        #   datetime.datetime,strptime : parse string into datetime object
        #   datetime.datetime.strftime : parse datetime object into string
        #
        #   Input : Attributes name empatica_hr dataframe, empatica_ibi dataframe, start_time and end_time
        #   Output : Sliced dataframe
        #######################################################################################################################
        
        # Define start_time and end_time object to compute the interval range
        start_time_object = datetime.datetime.strptime(start_time, '%H:%M:%S')
        end_time_object = datetime.datetime.strptime(end_time, '%H:%M:%S')
        
        # Parse datetime.datetime object into datetime.timedelta object for apply minus signs
        #   *** Can accept the microsecnonds but this won't use to be the index column
        start_time_timedelta = datetime.timedelta(hours=start_time_object.hour, minutes=start_time_object.minute, 
                                                  seconds=start_time_object.second, microseconds=start_time_object.microsecond)
        end_time_timedelta = datetime.timedelta(hours=end_time_object.hour, minutes=end_time_object.minute, 
                                                seconds=end_time_object.second, microseconds=end_time_object.microsecond)
        
        # Get the time interval between end_time and start_time
        self.time_interval = end_time_timedelta - start_time_timedelta
        
        # Slicing both hr and ibi using start_time and end_time
        self.empatica_hr = self.empatica_hr[start_time_object.time():end_time_object.time()]
        self.empatica_ibi = self.empatica_ibi[start_time_object.time():end_time_object.time()]

        

"""        
filename_hr = '../psg_experiments/Ex1/ex1_Empatica_1542378987_A019E6_2561-11-16_21-53-48/HR.csv'
filename_ibi = '../psg_experiments/Ex1/ex1_Empatica_1542378987_A019E6_2561-11-16_21-53-48/IBI.csv'

PreprocessingEmpatica = PreprocessingEmpatica(filename_hr, filename_ibi)
PreprocessingEmpatica.add_timestamp_and_preprocess_hr_data()
PreprocessingEmpatica.add_timestamp_and_preprocess_ibi_data()

x = PreprocessingEmpatica.empatica_hr
y = PreprocessingEmpatica.empatica_ibi

"""
"""
    
empatica_data_hr['Time'] = time_list
empatica_data_hr = empatica_data_hr[['Time', 'Heart rate']]



start_time = empatica_data_hr.iloc[0]['Time']
end_time = empatica_data_hr.iloc[-1]['Time']
time_interval = end_time - start_time
print("Interesting time interval [" + str(start_time.time()) + ',' + str(end_time.time()) + '] : ' + str(time_interval))
"""



""" Compare and empatica code
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pytz
import datetime

filename = '../psg_experiments/Ex2/ex2_Empatica_1542381668_A019E6_2561-11-16_22-18-48/HR.csv'
empatica_data_hr = pd.read_csv(filename, header=None, names=['Heart rate'])

utc_datetime = datetime.datetime.fromtimestamp(empatica_data_hr['Heart rate'][0])

# Get sampling rate from second line of HR.csv files
sampling_rate = empatica_data_hr['Heart rate'][1]

# Slice the timestamp row and sampling rate row out
empatica_data_hr = empatica_data_hr.loc[2:, :]
time_list = []

for i in range(0, len(empatica_data_hr)): 
    utc_datetime += datetime.timedelta(seconds=1/sampling_rate)
    time_list.append(utc_datetime)
    
empatica_data_hr['Time'] = time_list
empatica_data_hr = empatica_data_hr[['Time', 'Heart rate']]



start_time = empatica_data_hr.iloc[0]['Time']
end_time = empatica_data_hr.iloc[-1]['Time']
time_interval = end_time - start_time
print("Interesting time interval [" + str(start_time.time()) + ',' + str(end_time.time()) + '] : ' + str(time_interval))

empatica_data_hr['Time'] = empatica_data_hr['Time'].apply(lambda x : datetime.datetime.time(x))
comparison_df = ecg_feature_df_interest_interval.set_index(ecg_feature_df_interest_interval.index).join(empatica_data_hr.set_index('Time'))

plt.scatter(comparison_df.index, comparison_df['Heart rate'])
plt.scatter(comparison_df.index, comparison_df['Channel 1_estimated_heart_rate_by_time'])
plt.scatter(comparison_df.index, comparison_df['Channel 2_estimated_heart_rate_by_time'])



from sklearn.metrics import mean_squared_error
import math

comparison_df = comparison_df.fillna(method='ffill')
meanSquaredError=mean_squared_error(comparison_df['Heart rate'], comparison_df['Channel 2_estimated_heart_rate_by_time'])
print("MSE:", meanSquaredError)
rootMeanSquaredError = math.sqrt(meanSquaredError)
print("RMSE:", rootMeanSquaredError)
"""
