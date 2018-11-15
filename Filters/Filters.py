from scipy import signal
import numpy as np
class Filters:
	def __init__(self,window_size, low, high):
		fs_Hz = 250;
		fn = fs_Hz/2
		self.filtered_data = np.array((window_size,1))
		

		#######################################
		# Filter Creation
		# -------------------------------------
		#
		# Create a filter using the scipy module,
		# based on specifications suggested by
		# Pan-Tompkins (bandpass from 5-15Hz)
		#
		#
		# 1) Establish constants:
		#		a) filter_order = 2
		#		b) high pass cutoff = 15Hz
		#		c) low pass cutoff = 5Hz
		# 2) Calculate the coefficients, store in variables

		filter_order = 4
		f_high = high
		f_low = low
		self.high_pass_coefficients = signal.butter(filter_order,f_low/fn, 'high')
		self.low_pass_coefficients = signal.butter(filter_order,f_high/fn, 'low')


	#######################################
	# Bandpass filter
	# -------------------------------------
	# Filter the data, using a bandpass of 
	# 5-15Hz.
	# 
	# Input: 
	#			the data buffer from Data_Buffer class
	# Output:
	#			filtered data as a numpy array

	def bandpass(self,data_buffer):
		high_passed = self.high_pass(data_buffer)
		low_passed = self.low_pass(high_passed)
		filtered_data = np.array(low_passed)
		return filtered_data

	def high_pass(self,data_buffer):
		[b1, a1] = [self.high_pass_coefficients[0],self.high_pass_coefficients[1]]
		high_passed = signal.filtfilt(b1,a1,data_buffer)
		return high_passed

	def low_pass(self,data_buffer):
		[b, a] = [self.low_pass_coefficients[0],self.low_pass_coefficients[1]]
		low_passed = signal.filtfilt(b,a,data_buffer)
		return low_passed
    
    
    #######################################
    # Notch filter - Bandstop filter
    # -------------------------------------
    # Filter the data using a bandpass of 
    # 50 Hz(Power supply noise)
    # Input:
    #           the data buffer from Data_Buffer class
    # Output:
    #           filtered data as a numpy array
    
    
    
    
	def notch_filter(self, data_buffer, hz='50'):
		# assumed sample rate of OpenBCI
		fs_Hz = 250.0

		# create the 60 Hz filter
		bp_stop_Hz = np.array([59.0, 61.0])
		b, a = signal.butter(2,bp_stop_Hz/(fs_Hz / 2.0), 'bandstop')
		    
		# create the 50 Hz filter
		bp2_stop_Hz = np.array([49, 51.0]) 
		b2, a2 = signal.butter(2,bp2_stop_Hz/(fs_Hz / 2.0), 'bandstop')

		# compute the frequency response
		w, h = signal.freqz(b,a,1000)   #60Hz
		w, h2 = signal.freqz(b2,a2,1000)    #50Hz

		if hz=='50':
		    band_stopped = signal.filtfilt(b2, a2, data_buffer)
		else:
		    band_stopped = signal.filtfilt(b, a, data_buffer)

		return band_stopped


