# Example of using the PreprocessingAndAggregateOpenBCI class, PreprocessingEmpatica class and CompareECGFeature class
import PreprocessingAndAggregateOpenBCI
import PreprocessingEmpatica
import matplotlib.pyplot as plt
import CompareECGFeature

#Main program 

# 1.OpenBCI part
# 1.1.Define important parameters
# Define filename of OpenBCI datasource
filename = '../reformed/ex2_OpenBCI-RAW-2561-11-16_22-18-48_reform.csv'
# Define file_mode
file_mode = 1   # 0 = GUI and Python script(has only timestamp), 1 = Python script ===> This will affect to extract date and clock from timestamp
# Define which channel to be preocess
process_channel=['Channel 1', 'Channel 2']

# 1.2.Instance the PreprocessingAndAggregateOpenBCI Object to preprocess the data
# This will work both of channel
preprocessing_and_aggregate_data = PreprocessingAndAggregateOpenBCI.PreprocessingAndAggregateOpenBCI(filename, file_mode, process_channel)
# Filter the data
ecg_data_filtered = preprocessing_and_aggregate_data.filter_function()
# Find the heart rate and apply peak detection
ecg_data_hr_rr = preprocessing_and_aggregate_data.extract_hr_rr()
# Estimate hr by rr_interval
ecg_data_estimated = preprocessing_and_aggregate_data.get_estimated_heart_rate_ibi_and_count_heart_rate_by_time()

# 1.3 Slice data into interest interval
# Get the possible time interval in data for ensure that your interest interval is able to reach
preprocessing_and_aggregate_data.get_time_interval()
# Get data and aggregate information only in interest time interval
# Define start_time and end_time of interest time interval
start_time = '22:22:30'
end_time = '22:34:37'
# Using the get_interest_interval_information method to slice the dataframe into the interest interval
ecg_feature_df_interest_interval, aggregate_interest_interval, time_interval = preprocessing_and_aggregate_data.get_interest_interval_information(ecg_data_estimated, start_time, end_time)
# Seperate each channel into each dataframe(Can be use to do pair-comparison)
ecg_feature_df_interest_interval_sep_channel = preprocessing_and_aggregate_data.get_feature_df_interest_interval_each_channel()

# Assign to the dataframe variable for any of use
ecg_feature_df_interest_interval_ch1 = ecg_feature_df_interest_interval_sep_channel[0]
ecg_feature_df_interest_interval_ch2 = ecg_feature_df_interest_interval_sep_channel[1]

# 2. Empatica part
# 2.1 Define Important parameters
# Define filename of Empatica datasource
filename_hr = '../psg_experiments/Ex2/ex2_Empatica_1542381668_A019E6_2561-11-16_22-18-48/HR.csv'
filename_ibi = '../psg_experiments/Ex2/ex2_Empatica_1542381668_A019E6_2561-11-16_22-18-48/IBI.csv'

# Instance the ProcessingEmpatica object
PreprocessingEmpatica = PreprocessingEmpatica.PreprocessingEmpatica(filename_hr, filename_ibi)

# 2.2 Use add_timestamp method to both data to add the timestamp(also apply to index for easy joining)
PreprocessingEmpatica.add_timestamp_and_preprocess_hr_data()
PreprocessingEmpatica.add_timestamp_and_preprocess_ibi_data()

# Get the possilbe time interval to make sure the interest time that we need is in the range
PreprocessingEmpatica.get_time_interval()
# 2.3 Slice the data into interest interval
PreprocessingEmpatica.get_df_interest_time_interval(start_time, end_time)

# Assing to the dataframe variable for any of use
empatica_hr = PreprocessingEmpatica.empatica_hr
empatica_ibi = PreprocessingEmpatica.empatica_ibi

# 3. Compare part
# 3.1 Instance the CompareECGFeature class to compare every source based on hr and ibi
comparison_ecg_feature = CompareECGFeature.CompareECGFeature(ecg_feature_df_interest_interval_ch1, ecg_feature_df_interest_interval_ch2, empatica_hr, empatica_ibi)

# 3.2 Call comparison method to join the dataframe of every source and can be use to plot or compare
# Contain the joining dataframe in comparison_df_<hr or ibi>
comparison_df_hr = comparison_ecg_feature.compare_hr_every_source()
comparison_df_ibi = comparison_ecg_feature.compare_ibi_every_source()

# Simple plot
comparison_ecg_feature.simple_plot_hr(comparison_df_hr)
comparison_ecg_feature.simple_plot_ibi(comparison_df_ibi)


"""
# Pair-comparison
plt.figure()
ecg_joined = ecg_feature_df_interest_interval_sep_channel[0].join(ecg_feature_df_interest_interval_sep_channel[1], on=ecg_feature_df_interest_interval_sep_channel[0].index)
plt.plot(ecg_joined[0:15].index, ecg_joined[0:15]['Channel 1_estimated_heart_rate_by_time'])
plt.plot(ecg_joined[0:15].index, ecg_joined[0:15]['Channel 2_estimated_heart_rate_by_time'])
"""