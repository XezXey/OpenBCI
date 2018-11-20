import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 

class CompareECGFeature:
    def __init__(self, ecg_feature_df_interest_interval_ch1, ecg_feature_df_interest_interval_ch2, empatica_hr, empatica_ibi):
        self.ecg_feature_df_interest_interval_ch1 = ecg_feature_df_interest_interval_ch1
        self.ecg_feature_df_interest_interval_ch2 = ecg_feature_df_interest_interval_ch2
        self.empatica_hr = empatica_hr
        self.empatica_ibi = empatica_ibi
        
    def compare_hr_every_source(self, need_nan=True):
        # Comparison class
        comparison_df_hr = self.ecg_feature_df_interest_interval_ch1[['Channel 1_estimated_heart_rate_by_time']]
        comparison_df_hr = comparison_df_hr.set_index(comparison_df_hr.index).join(self.ecg_feature_df_interest_interval_ch2['Channel 2_estimated_heart_rate_by_time'])
        comparison_df_hr = comparison_df_hr.set_index(comparison_df_hr.index).join(self.empatica_hr.set_index('clock'))
        #comparison_df_hr = comparison_df_hr.set_index(comparison_df_hr.index).join(self.ecg_feature_df_interest_interval_ch2.set_index(self.ecg_feature_df_interest_interval_ch2.index))
        if need_nan == False:
            comparison_df_hr = comparison_df_hr.dropna()

        #comparison_df_hr = comparison_df[150:180]
        return comparison_df_hr
        
    def compare_ibi_every_source(self, need_nan=True):
        # Comparison class
        comparison_df_ibi = self.ecg_feature_df_interest_interval_ch1[['Channel 1_rr_interval(IBI)']]
        comparison_df_ibi = comparison_df_ibi.set_index(comparison_df_ibi.index).join(self.ecg_feature_df_interest_interval_ch2['Channel 2_rr_interval(IBI)'])
        comparison_df_ibi = comparison_df_ibi.set_index(comparison_df_ibi.index).join(self.empatica_ibi)
        if need_nan == False:
            comparison_df_ibi = comparison_df_ibi.dropna()
        #comparison_df_ibi = comparison_df_ibi[150:180]
        return comparison_df_ibi


    def simple_plot_hr(self, comparison_df_hr):
            plt.figure()
            plt.title('Comparison between 3 source')
            plt.ylabel('Heart Rate(bpm)')
            plt.plot(comparison_df_hr.index, comparison_df_hr['Channel 1_estimated_heart_rate_by_time'])
            plt.xticks(rotation=70)
            plt.plot(comparison_df_hr.index, comparison_df_hr['Channel 2_estimated_heart_rate_by_time'])
            plt.plot(comparison_df_hr.index, comparison_df_hr['heart_rate'])
            plt.legend()
        
        
    def simple_plot_ibi(self, comparison_df_ibi):
            plt.figure()
            plt.title('Comparison between 3 source')
            plt.ylabel('RR_Interval')
            plt.plot(comparison_df_ibi.index, comparison_df_ibi['Channel 1_rr_interval(IBI)'])
            plt.xticks(rotation=70)
            plt.plot(comparison_df_ibi.index, comparison_df_ibi['Channel 2_rr_interval(IBI)'])
            plt.plot(comparison_df_ibi.index, comparison_df_ibi['rr_interval'])
            plt.legend()