import pandas as pd
import numpy as np
import datetime

class PreprocessingEmpatica:
    #####################################################################################################
    # PreprocessingEmpatica class
    def __init__(self, filename_hr, filename_ibi):
        
        self.filename_hr = filename_hr
        self.filename_ibi = filename_ibi
        
        self.empatica_hr = pd.read_csv(self.filename_hr, names=['heart_rate'], header=None)        
        self.empatica_ibi = pd.read_csv(self.filename_ibi, names=['peak_pos', 'rr_interval'], header=None) 
       
    
    def get_time_list(self, empatica_data, utc_datetime):
        time_list = []
        for i in range(0, len(empatica_data)): 
            utc_datetime += datetime.timedelta(seconds=1/self.sampling_rate_hr)
            time_list.append(utc_datetime)
        return time_list

    def add_timestamp_and_preprocess_hr_data(self):
        utc_datetime_hr = datetime.datetime.fromtimestamp(self.empatica_hr['heart_rate'][0])
        self.sampling_rate_hr = self.empatica_hr['heart_rate'][1]    ## Get sampling rate from second line of HR.csv files
        self.empatica_hr = self.empatica_hr.loc[2:, :]
        self.empatica_hr = self.empatica_hr.reset_index(drop=True)

        time_list = self.get_time_list(self.empatica_hr, utc_datetime_hr)
        
        self.empatica_hr['Timestamp'] = time_list
        self.empatica_hr['date'] = self.empatica_hr['Timestamp'].apply(lambda each_time : each_time.date())
        self.empatica_hr['clock'] = self.empatica_hr['Timestamp'].apply(lambda each_time : each_time.time())
        self.empatica_hr = self.empatica_hr.set_index(self.empatica_hr['clock'])



        
    def add_timestamp_and_preprocess_ibi_data(self):
        utc_datetime_ibi = datetime.datetime.fromtimestamp(self.empatica_ibi['peak_pos'][0])
        self.empatica_ibi = self.empatica_ibi.loc[1:, :]
        self.empatica_ibi = self.empatica_ibi.reset_index(drop=True)
        time_increment_from_initial = np.diff(self.empatica_ibi['peak_pos'])
        time_increment_from_initial = np.insert(time_increment_from_initial, 0, 0)
        #print(len(time_increment_from_initial))
        #print(len(self.empatica_ibi))
        time_list = []
        for i in range(0, len(time_increment_from_initial)):
            utc_datetime_ibi += datetime.timedelta(seconds=time_increment_from_initial[i])
            time_list.append(utc_datetime_ibi)
        
        self.empatica_ibi['Timestamp'] = time_list
        self.empatica_ibi['date'] = self.empatica_ibi['Timestamp'].apply(lambda each_time : each_time.date())
        self.empatica_ibi['clock'] = self.empatica_ibi['Timestamp'].apply(lambda each_time : each_time.time())
        self.empatica_ibi = self.empatica_ibi.set_index(self.empatica_ibi['clock'].apply(lambda each_time : each_time.replace(microsecond=0)))

        
    def get_time_interval(self):
        return dict(empatica_hr_time_interval = str(self.empatica_hr.iloc[0]['clock']) + ' to ' + str(self.empatica_hr.iloc[-1]['clock']), empatica_ibi_time_interval = str(self.empatica_ibi.iloc[0]['clock']) + ' to ' + str(self.empatica_ibi.iloc[-1]['clock']))
        
    def get_df_interest_time_interval(self, start_time, end_time):
         # Define start_time and end_time object to compute the interval range
        start_time_object = datetime.datetime.strptime(start_time, '%H:%M:%S')
        end_time_object = datetime.datetime.strptime(end_time, '%H:%M:%S')
        
        # Parse datetime.datetime object into datetime.timedelta object for apply minus signs
        start_time_timedelta = datetime.timedelta(hours=start_time_object.hour, minutes=start_time_object.minute, 
                                                  seconds=start_time_object.second, microseconds=start_time_object.microsecond)
        end_time_timedelta = datetime.timedelta(hours=end_time_object.hour, minutes=end_time_object.minute, 
                                                seconds=end_time_object.second, microseconds=end_time_object.microsecond)
        
        self.time_interval = end_time_timedelta - start_time_timedelta
        
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
