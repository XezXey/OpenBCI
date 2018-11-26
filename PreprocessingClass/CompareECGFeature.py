import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from sklearn.metrics import mean_squared_error

class CompareECGFeature:
    ##########################################################################################################################
    # CompareECGFeature class
    # Sources : HR - 4 sources ==> Chest(Baseline), Wrist, Empatica_HR, Empatica_estimated_hr
    #           IBI - 3 sources ==> Chest(Baseline), Wrist, Empatica_ibi
    # 1. Compare heart rate from every source
    #   1.1 Use join on index from 3 source dataframe
    # 2. Compare ibi from every source
    #   2.1 Use join on index from 3 source dataframe
    # *** Join use the Channel 1(Chest) as a baseline
    # 3. Simple plot hr from every source
    # 4. Simple plot ibi from every source
    # 5. Calculate RMSE from every source with Channel 1 as a baseline both of HR and IBI
    # 6. Can joining the Empatica_estimated_heart_rate_by_time to the comparison_df_hr
    ##################################################################################################################################################
    def __init__(self, ecg_feature_df_interest_interval_ch1, ecg_feature_df_interest_interval_ch2, empatica_hr, empatica_ibi):
        # Initialization Attributes
        self.ecg_feature_df_interest_interval_ch1 = ecg_feature_df_interest_interval_ch1    # Contain features df of ecg in interest interval of Ch1
        self.ecg_feature_df_interest_interval_ch2 = ecg_feature_df_interest_interval_ch2    # Contain features df of ecg in interest interval of Ch2
        self.empatica_hr = empatica_hr    # Contain empatica_hr dataframe
        self.empatica_ibi = empatica_ibi    # Contain empatica_ibi dataframe
        
    def compare_hr_every_source(self, need_nan=True):
        ##################################################################################################################################
        # Comparison heart rate from every source class
        # 1. Joining every dataframe of ['estimated_heart_rate_by_time'] column and using Channel 1 as a baseline on ['clock'] column 
        # 2. Can select mode to remove 'Nan' or not
        #
        #   Input : Attributes name ecg_feature_df_interest_interval_ch1, ecg_feature_df_interest_interval_ch2 and empatica_hr
        #   Output : comparison_df_hr and applying join between 3 source
        ###################################################################################################################################
        
        comparison_df_hr = self.ecg_feature_df_interest_interval_ch1[['Channel 1_estimated_heart_rate_by_time']]    # Use Ch1 as a baseline
        comparison_df_hr = comparison_df_hr.set_index(comparison_df_hr.index).join(self.ecg_feature_df_interest_interval_ch2['Channel 2_estimated_heart_rate_by_time']) # Joining dataframe Ch1 with Ch2 using Ch1 index(aka. 'clock')
        comparison_df_hr = comparison_df_hr.set_index(comparison_df_hr.index).join(self.empatica_hr.set_index('clock')) # Joining dataframe Ch1(+Ch2) with empatica_hr on Ch1(+Ch2) index(aka. 'clock')
        #comparison_df_hr = comparison_df_hr.set_index(comparison_df_hr.index).join(self.ecg_feature_df_interest_interval_ch2.set_index(self.ecg_feature_df_interest_interval_ch2.index))
        
        # Dropping Nan control by need_nan value
        if need_nan == False:
            comparison_df_hr = comparison_df_hr.dropna()

        # comparison_df_hr = comparison_df[150:180] ===> Can edit this to easily slice of data
        return comparison_df_hr
        
    def compare_ibi_every_source(self, need_nan=True):
        ##################################################################################################################################
        # Comparison IBI from every source class
        # 1. Joining every dataframe of ['rr_interval(IBI)'] column and using Channel 1 as a baseline on ['clock'] column 
        # 2. Can select mode to remove 'Nan' or not
        #
        #   Input : Attributes name ecg_feature_df_interest_interval_ch1, ecg_feature_df_interest_interval_ch2 and empatica_ibi
        #   Output : comparison_df_hr and applying join between 3 source
        ##################################################################################################################################
        
        comparison_df_ibi = self.ecg_feature_df_interest_interval_ch1[['Channel 1_rr_interval(IBI)']]    # Use Ch1 as a baseline
        comparison_df_ibi = comparison_df_ibi.set_index(comparison_df_ibi.index).join(self.ecg_feature_df_interest_interval_ch2['Channel 2_rr_interval(IBI)'])    # Joining dataframe Ch1 with Ch2 using Ch1 index(aka. 'clock')
        comparison_df_ibi = comparison_df_ibi.set_index(comparison_df_ibi.index).join(self.empatica_ibi)    # Joining dataframe Ch1(+Ch2) with empatica_ibi on Ch1(+Ch2) index(aka. 'clock')
        
        # Dropping Nan control by neen_nan value
        if need_nan == False:
            comparison_df_ibi = comparison_df_ibi.dropna()
            
        #comparison_df_ibi = comparison_df_ibi[150:180] ===> Can edit this to easily slice of data
        return comparison_df_ibi


    def simple_plot_hr(self, comparison_df_hr):
        ###################################################################################################################################
        # Simple plot heart rate
        # 1. Plotting graph from every channel
        #   1.1 x-axis is time(s)
        #   1.2 y-axis is heart rate(bpm)
        # *** Mention
        #   Plotting by use the interest interval dataframe and the dataframe need to called both of compare method first(Joined dataframe)
        #
        #   Input : comparison_df_hr
        #   Output : Beautiful graph
        ###################################################################################################################################
        plt.figure(figsize=(20, 10))    # Plot in a new figure
        plt.title('HR - Comparison between 3 source')    # Title of graph
        plt.ylabel('Heart Rate(bpm)')    # Name of y-axis
        plt.xticks(rotation=70)    # Rotate the name in x-axis 70 degree
        plt.plot(comparison_df_hr.index, comparison_df_hr['Channel 1_estimated_heart_rate_by_time'], linewidth=3.0, marker='x', markersize=10, color='r', label='OpenBCI_CH1_HR')    # Plotting heart rate the OpenBCI_Ch1 dataframe
        plt.plot(comparison_df_hr.index, comparison_df_hr['Channel 2_estimated_heart_rate_by_time'], linewidth=3.0, marker='*', markersize=10, color='b', label='OpenBCI_CH2_HR')    # Plotting heart rate the OpenBCI_Ch2 dataframe
        plt.plot(comparison_df_hr.index, comparison_df_hr['heart_rate'], linewidth=3.0, marker='+', markersize=10, color='g', label='Empatica_HR')    # Plotting heart rate from the empatica
        plt.plot(comparison_df_hr.index, comparison_df_hr['Empatica_estimated_heart_rate_by_time'], linewidth=3.0, marker='1', markersize=10, color='y', label='Empatica_HR_Estimated')
        plt.legend()    # Showing the graph line name
        
        
    def simple_plot_ibi(self, comparison_df_ibi):
        ###################################################################################################################################
        # Simple plot ibi
        # 1. Plotting graph from every channel
        #   1.1 x-axis is time(s)
        #   1.2 y-axis is heart rate(bpm)
        # *** Mention
        #   Plotting by use the interest interval dataframe and the dataframe need to called both of compare method first(Joined dataframe)
        #
        #   Input : comparison_df_hr
        #   Output : Beautiful graph
        ###################################################################################################################################
        plt.figure(figsize=(20, 10))    # Plot in a new figure
        plt.title('IBI - Comparison between 3 source')    # Title of graph
        plt.ylabel('RR_Interval')    # Name of y-axis        
        plt.xticks(rotation=70)    # Rotate the name in x-axis 70 degree
        #plt.plot(comparison_df_ibi[['Channel 1_rr_interval(IBI)', 'Channel 2_rr_interval(IBI)', 'rr_interval']])
        plt.plot(comparison_df_ibi.index, comparison_df_ibi['Channel 1_rr_interval(IBI)'], linewidth=3.0, marker='x', markersize=10, color='r', label='OpenBCI_CH1_IBI')    # Plotting heart rate the OpenBCI_Ch1 dataframe
        plt.plot(comparison_df_ibi.index, comparison_df_ibi['Channel 2_rr_interval(IBI)'], linewidth=3.0, marker='*', markersize=10, color='b', label='OpenBCI_CH2_IBI')    # Plotting heart rate the OpenBCI_Ch2 dataframe
        plt.plot(comparison_df_ibi.index, comparison_df_ibi['rr_interval'], linewidth=3.0, marker='+', markersize=10, color='g', label='Empatica_IBI')    # Plotting heart rate from the empatica
        plt.legend()    # Showing the graph line name
        
    #def simple_plot_peak_pos(self, comparison_df_)    
        
    def cal_rmse(self, comparison_df, signal):
        ###################################################################################################################################
        # Fidning RMSE
        # 1. Calculate root mean square error(RMSE) between pair of baseline and other channel following signal that recieved
        #
        #   Input : comparison dataframe that contain all channel of sources and type of signal('ibi' or 'hr')
        #   Output : dictionary of rmse value
        ###################################################################################################################################
        comparison_df = comparison_df.dropna()
        if signal == 'hr':
            rmse_hr_ch1_ch2 = math.sqrt(mean_squared_error(comparison_df['Channel 1_estimated_heart_rate_by_time'], comparison_df['Channel 2_estimated_heart_rate_by_time']))
            rmse_hr_ch1_heart_rate = math.sqrt(mean_squared_error(comparison_df['Channel 1_estimated_heart_rate_by_time'], comparison_df['heart_rate']))
            rmse_hr_ch1_empat = math.sqrt(mean_squared_error(comparison_df['Channel 1_estimated_heart_rate_by_time'], comparison_df['Empatica_estimated_heart_rate_by_time']))
            return dict(ch1_ch2_hr=rmse_hr_ch1_ch2, ch1_empt_hr=rmse_hr_ch1_heart_rate, ch1_empt_est=rmse_hr_ch1_empat)
        elif signal == 'ibi':
            rmse_ibi_ch1_ch2 = math.sqrt(mean_squared_error(comparison_df['Channel 1_rr_interval(IBI)'], comparison_df['Channel 2_rr_interval(IBI)']))
            rmse_ibi_ch1_empt = math.sqrt(mean_squared_error(comparison_df['Channel 1_rr_interval(IBI)'], comparison_df['rr_interval']))
            return (dict(ch1_ch2_ibi=rmse_ibi_ch1_ch2, ch1_empt_ibi=rmse_ibi_ch1_empt))
                   
    def esti_empt_hr_and_join_all_hr(self, comparison_df_ibi, comparison_df_hr):
        ####################################################################################################################################
        # Joining the table between Empatica_estimated_heart_rate and OpenBCI_estimated_heart_rate()
        # 1. We obtained the esitmated heart rate from empatica by calculate using 60/rr_interval so the estimated result will out.
        # 2. We need to join again between Empatica_estimated_heart_rate_by_time columns and the comparison_hr_df
        #   Input : comparison_df_ibi, comparison_df_hr
        #   Output : comparison_all_hr that have all heart rate from every source
        ####################################################################################################################################
        
        comparison_df_ibi['Empatica_estimated_heart_rate_by_time'] = 60/(comparison_df_ibi['rr_interval'])
        comparison_all_hr = comparison_df_ibi[['Empatica_estimated_heart_rate_by_time']].join(comparison_df_hr)
        return comparison_all_hr
    
    
    