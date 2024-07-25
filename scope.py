import pyvisa
import numpy as np
import time
import matplotlib.pyplot as plt

# Initialize the resource manager and connect to the oscilloscope
rm = pyvisa.ResourceManager()
instruments = rm.list_resources()
print(f"Connected instruments: {instruments}")

oscilloscope_ip = '192.168.1.10'
scope_name = f'TCPIP0::{oscilloscope_ip}::INSTR'
scope = rm.open_resource(scope_name)
scope.timeout = 100000  # Increase timeout to 20 seconds
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls')
channel = 'CH1'
print(scope.query('*idn?'))

# Reset the oscilloscope and configure horizontal settings
scope.write('*rst')
scope.write('header 0')
t1 = time.perf_counter()
r = scope.query('*opc?')
t2 = time.perf_counter()
print('reset time: {}'.format(t2 - t1))

scope.write('HORIZONTAL:MODE MANUAL')
desired_time_window = 11  # 11 secondsT
sampling_rate = 1e5  # 1000 Sa/s
scope.write(f'Horizontal:MODE:SAMPLERATE {sampling_rate}')
record_length = int(sampling_rate * desired_time_window)
scope.write(f'HORIZONTAL:RECORDLENGTH {record_length}')
print(scope.query('HORIZONTAL?'))

# Turn on Channel
scope.write(f'SELect:{channel} ON')

# Configure Channel settings
scope.write(f':{channel}:SCAle 0.0001')  # V/div
scope.write(f':{channel}:COUP AC')  # AC or DC
scope.write(f'{channel}:PROBEFunc:EXTAtten 1')  # 1x or 10x
scope.write('acquire:mode HIRES')

# Debugging prints
print(scope.query(f':{channel}:SCAle?'))
print(scope.query(f':{channel}:COUPling?'))

# Set and verify data source
scope.write(f'data:source {channel}')
time.sleep(0.1)  # Short delay
current_source = scope.query('DATA:SOURCE?').strip()
print(f"Current data source set to: {current_source}")

# Check horizontal settings
print(scope.query('HORIZONTAL:RECORDLENGTH?'))
print(scope.query('HORIZONTAL:SAMPLERATE?'))

t3 = time.perf_counter()
r = scope.query('*opc?')
t4 = time.perf_counter()
print('autoset time: {} s'.format(t4 - t3))

# Configure data and acquisition settings
scope.write('data:encdg SRIBINARY')
scope.write('data:start 1')
scope.write(f'data:stop {record_length}')
scope.write('wfmoutpre:byt_n 1')

scope.write('acquire:state 0')
scope.write('acquire:stopafter SEQUENCE')
scope.write('acquire:state 1')

print("Starting acquisition...")
t5 = time.perf_counter()
try:
    r = scope.query('*opc?')
except pyvisa.errors.VisaIOError as e:
    print(f"Timeout error during acquisition: {e}")
t6 = time.perf_counter()
print('acquire time: {} s'.format(t6 - t5))

# Transfer waveform data from the oscilloscope
t7 = time.perf_counter()
bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)
t8 = time.perf_counter()
print('transfer time: {} s'.format(t8 - t7))

# Retrieve scaling factors
tscale = float(scope.query('wfmoutpre:xincr?'))
tstart = float(scope.query('wfmoutpre:xzero?'))
vscale = float(scope.query('wfmoutpre:ymult?'))
voff = float(scope.query('wfmoutpre:yzero?'))
vpos = float(scope.query('wfmoutpre:yoff?'))

r = int(scope.query('*esr?'))
print('event status register: 0b{:08b}'.format(r))
r = scope.query('allev?').strip()
print('all event messages: {}'.format(r))

scope.close()
rm.close()

# Create scaled vectors for the time-domain plot
total_time = tscale * record_length
tstop = tstart + total_time
scaled_time = np.linspace(tstart, tstop, num=record_length, endpoint=False)
unscaled_wave = np.array(bin_wave, dtype='double')
scaled_wave = (unscaled_wave - vpos) * vscale + voff

# Adjust the vertical range to show the entire signal
vertical_range = 2  # Adjust this value based on the expected signal range

# Crop data to 10 seconds
record_length_cropped = int(sampling_rate * 10)  # 10 seconds
scaled_time_cropped = scaled_time[:record_length_cropped]
scaled_wave_cropped = scaled_wave[:record_length_cropped]

# Perform FFT and prepare frequency-domain data for the cropped data
fft_result = np.fft.fft(scaled_wave_cropped)
fft_freq = np.fft.fftfreq(record_length_cropped, d=tscale)
fft_magnitude = np.abs(fft_result) / record_length_cropped

# Plot time-domain signal for cropped data
plt.figure(figsize=(12, 6))
plt.plot(scaled_time_cropped, scaled_wave_cropped)
plt.title(f'{channel}')
plt.xlabel('Time (seconds)')
plt.ylabel('Voltage (volts)')
plt.ylim(-vertical_range, vertical_range)  # Adjust the vertical range
plt.grid(True)
plt.show()

# Plot frequency-domain signal for cropped data
plt.figure(figsize=(12, 6))
plt.plot(fft_freq[:record_length_cropped // 2], fft_magnitude[:record_length_cropped // 2])
plt.title('FFT')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.grid(True)
plt.show()

print("\nEnd of demonstration")