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

# Import Raw signal to apply filter later
print("Loading data...", end='')
ecg_data = pd.read_csv('../reformed/OpenBCI-RAW-2561-11-15_16-38-08_Analyze_finale_reform.csv')
ecg_data = ecg_data[['Time', 'Timestamp', 'Channel 1']]


# 1. Power supply filter(50 Hz) : Apply Notch filter to signal
print("Apply notch filter...", end='')
filter_signal = Filters.Filters(window_size=10, low=0.67, high=5)
ecg_data_notched_50 = filter_signal.notch_filter(ecg_data['Channel 1'], hz='50')
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


# 5. Visualization
# frequency is 250Hz
# number_of_data = 250 * x (seconds)

print("Visualization")
# 1. Plotting raw data
plt.figure()
plt.plot(ecg_data['Channel 1'][2500:5000])
plt.title('ECG Raw data')
plt.xlabel('Time(s)')
plt.ylabel('Amplitude(uV)')


# 2. Plotting data after apply 50Hz notch filter
plt.figure()
plt.plot(ecg_data_notched_50[2500:5000])
plt.title('ECG with Notched filter(50 Hz)')
plt.xlabel('Time(s)')
plt.ylabel('Amplitude(uV)')

# 3. Plotting data after apply breathing filter(0.5 Hz)
plt.figure()
plt.plot(ecg_data_breathing[2500:5000])
plt.title('ECG with Breathing filter(0.5 Hz)')
plt.xlabel('Time(s)')
plt.ylabel('Amplitude(uV)')

# 4. Plotting data after apply R-peak filter(15-20 Hz)
plt.figure()
plt.plot(ecg_data_r_peak[2500:5000])
plt.title('ECG with R-Peak filter(15-20 Hz)')
plt.xlabel('Time(s)')
plt.ylabel('Amplitude(uV)')

# 5. Plotting data after apply ECG range filter(0.67-5 Hz)
plt.figure()
plt.plot(ecg_finale_data[2500:4000])
plt.title('ECG with applied ECG range filter')
plt.xlabel('Time(s)')
plt.ylabel('Amplitude(uV)')



ecg_analyze_interval = ecg_finale_data[35000:37500]
peak, _ = find_peaks(ecg_analyze_interval, distance=150)
diff = np.diff(peak)

plt.figure()
plt.plot(ecg_analyze_interval)
plt.plot(peak, ecg_finale_data[peak], "x")
plt.title('Apply find peaks algorithm')
plt.xlabel('Time(s)')
plt.ylabel('Amplitude(uV)')

print('Heart rate in ' +  str(len(ecg_analyze_interval)/250) + ' seconds = ' + str(len(peak)))
