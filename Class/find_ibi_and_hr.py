import PreprocessingAndAggregateOpenBCI
import PreprocessingEmpatica
import matplotlib.pyplot as plt
import CompareECGFeature

#Main program 
filename = '../reformed/ex2_OpenBCI-RAW-2561-11-16_22-18-48_reform.csv'
file_mode = 1   # 0 = GUI and Python script(has only timestamp), 1 = Python script ===> This will affect to extract date and clock from timestamp
process_channel=['Channel 1', 'Channel 2']
preprocessing_and_aggregate_data = PreprocessingAndAggregateOpenBCI.PreprocessingAndAggregateOpenBCI(filename, file_mode, process_channel)
ecg_data_filtered = preprocessing_and_aggregate_data.filter_function()
ecg_data_hr_rr = preprocessing_and_aggregate_data.extract_hr_rr()
ecg_data_estimated = preprocessing_and_aggregate_data.get_estimated_heart_rate_ibi_and_count_heart_rate_by_time()

# Get the possible time interval in data for ensure that your interest interval is able to reach
preprocessing_and_aggregate_data.get_time_interval()

# Get data and aggregate information only in interest time interval
# Define start_time and end_time of interest time interval
start_time = '22:22:30'
end_time = '22:34:37'
ecg_feature_df_interest_interval, aggregate_interest_interval, time_interval = preprocessing_and_aggregate_data.get_interest_interval_information(ecg_data_estimated, start_time, end_time)

ecg_feature_df_interest_interval_sep_channel = preprocessing_and_aggregate_data.get_feature_df_interest_interval_each_channel()

ecg_feature_df_interest_interval_ch1 = ecg_feature_df_interest_interval_sep_channel[0]
ecg_feature_df_interest_interval_ch2 = ecg_feature_df_interest_interval_sep_channel[1]

plt.figure()
ecg_joined = ecg_feature_df_interest_interval_sep_channel[0].join(ecg_feature_df_interest_interval_sep_channel[1], on=ecg_feature_df_interest_interval_sep_channel[0].index)
plt.plot(ecg_joined[0:15].index, ecg_joined[0:15]['Channel 1_estimated_heart_rate_by_time'])
plt.plot(ecg_joined[0:15].index, ecg_joined[0:15]['Channel 2_estimated_heart_rate_by_time'])

filename_hr = '../psg_experiments/Ex2/ex2_Empatica_1542381668_A019E6_2561-11-16_22-18-48/HR.csv'
filename_ibi = '../psg_experiments/Ex2/ex2_Empatica_1542381668_A019E6_2561-11-16_22-18-48/IBI.csv'

PreprocessingEmpatica = PreprocessingEmpatica.PreprocessingEmpatica(filename_hr, filename_ibi)
PreprocessingEmpatica.add_timestamp_and_preprocess_hr_data()
PreprocessingEmpatica.add_timestamp_and_preprocess_ibi_data()

PreprocessingEmpatica.get_time_interval()
PreprocessingEmpatica.get_df_interest_time_interval(start_time, end_time)

empatica_hr = PreprocessingEmpatica.empatica_hr
empatica_ibi = PreprocessingEmpatica.empatica_ibi


comparison_ecg_feature = CompareECGFeature.CompareECGFeature(ecg_feature_df_interest_interval_ch1, ecg_feature_df_interest_interval_ch2, empatica_hr, empatica_ibi)
comparison_df_hr = comparison_ecg_feature.compare_hr_every_source()
comparison_df_ibi = comparison_ecg_feature.compare_ibi_every_source()

comparison_ecg_feature.simple_plot_hr(comparison_df_hr)
comparison_ecg_feature.simple_plot_ibi(comparison_df_ibi)


"""
# Comparison class
comparison_df = ecg_feature_df_interest_interval_ch1.set_index(ecg_feature_df_interest_interval_ch1.index).join(empatica_hr.set_index('clock'))
comparison_df = comparison_df.set_index(comparison_df.index).join(ecg_feature_df_interest_interval_ch2.set_index(ecg_feature_df_interest_interval_ch2.index))
comparison_df = comparison_df.dropna()
comparison_df = comparison_df[150:180]
"""