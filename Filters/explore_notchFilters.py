import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pandas as pd
from scipy.signal import find_peaks
from scipy.misc import electrocardiogram

ecg_data = pd.read_csv('../reformed/OpenBCI-RAW-2561-11-11_17-53-5_Analyze10_reform.csv')

window = 10
c = [1, 2, 3]
ecg_data['Channel 1'] = (ecg_data['Channel 1'] - np.mean(ecg_data['Channel 1'] * window)/np.mean(window)) * window

import Filters

plt.title("Signal before filter")
plt.xlabel('Sample')
plt.ylabel('Amplitude(uV)')
plt.plot(ecg_data['Channel 1'])


filter_signal = Filters.Filters(window_size=60, low=15, high=20)

ecg_data_notched_50 = filter_signal.notch_filter(ecg_data['Channel 1'], hz='50')

plt.plot(ecg_data_bandpass[500:25000])
plt.plot(ecg_data_notched_50[1000:7500])


filter_signal_2 = Filters.Filters(window_size=60, low=0.5, high=5)

b, a = signal.butter(2, 0.5, 'high', analog=True)
ecg_data_highpass_0p5 = signal.filtfilt(b, a, ecg_data_notched_50)
plt.plot(ecg_data_highpass_0p5[1000:7500])

ecg_data_highpass15 = filter_signal.high_pass(ecg_data_highpass_0p5)
ecg_data_lowpass20 = filter_signal.low_pass(ecg_data_highpass15)
plt.plot(ecg_data_lowpass20[100:15100])
plt.plot(ecg_data_bandpass[1000:1])

peak, _ = find_peaks(ecg_data_lowpass20[100:700], distance=50)
diff = np.diff(peak)

plt.plot(ecg_data_lowpass20[100:700])
plt.plot(peak, ecg_data_lowpass20[peak], "x")


ecg = electrocardiogram()
plt.plot(ecg[100:2000])
peaks, _ = find_peaks(ecg[100:2100], distance=100)
plt.plot(peaks, ecg[peaks], 'x')