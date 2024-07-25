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
scope.timeout = 100000  # Increase timeout to 100 seconds
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls')
channels = ['CH1', 'CH2', 'CH3','CH4']
print(scope.query('*idn?'))

# Define settings for each channel
channel_settings = {
    'CH1': {'sampling_rate': 1e5, 'v_div': 0.1}, #sin +
    'CH2': {'sampling_rate': 1e5, 'v_div': 0.1}, #sin -
    'CH3': {'sampling_rate': 1e5, 'v_div': 0.1}, #cos +
    'CH4': {'sampling_rate': 1e5, 'v_div': 0.1}  #cos -
}

# Define the multiplication factor
factor = 100000 / 90  # pm/degree

# Reset the oscilloscope and configure horizontal settings
scope.write('*rst')
scope.write('header 0')
t1 = time.perf_counter()
r = scope.query('*opc?')
t2 = time.perf_counter()
print('reset time: {}'.format(t2 - t1))

# Turn on Channels and configure settings
for channel, settings in channel_settings.items():
    scope.write(f'SELect:{channel} ON')
    scope.write(f':{channel}:SCAle {settings["v_div"]}')  # V/div
    scope.write(f':{channel}:COUP AC')  # AC or DC
    scope.write(f'{channel}:PROBEFunc:EXTAtten 1')  # 1x or 10x

scope.write('acquire:mode HIRES')

# Debugging prints
for channel in channels:
    print(scope.query(f':{channel}:SCAle?'))
    print(scope.query(f':{channel}:COUPling?'))

# Configure horizontal settings for each channel
desired_time_window = 11  # 11 seconds
for channel, settings in channel_settings.items():
    scope.write(f'HORIZONTAL:MODE MANUAL')
    sampling_rate = settings['sampling_rate']
    record_length = int(sampling_rate * desired_time_window)
    scope.write(f'HORIZONTAL:MODE:SAMPLERATE {sampling_rate}')
    scope.write(f'HORIZONTAL:RECORDLENGTH {record_length}')
    print(scope.query(f'HORIZONTAL?'))

t3 = time.perf_counter()
r = scope.query('*opc?')
t4 = time.perf_counter()
print('autoset time: {} s'.format(t4 - t3))

# Configure data and acquisition settings
scope.write('data:encdg SRIBINARY')
scope.write('data:start 1')
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

waveforms = {}

# Transfer waveform data from the oscilloscope for each channel
for channel, settings in channel_settings.items():
    scope.write(f'data:source {channel}')
    time.sleep(0.1)  # Short delay
    current_source = scope.query('DATA:SOURCE?').strip()
    print(f"Current data source set to: {current_source}")

    record_length = int(settings['sampling_rate'] * desired_time_window)
    scope.write(f'data:stop {record_length}')

    t7 = time.perf_counter()
    bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)
    t8 = time.perf_counter()
    print(f'transfer time for {channel}: {t8 - t7} s')

    # Retrieve scaling factors
    tscale = float(scope.query('wfmoutpre:xincr?'))
    tstart = float(scope.query('wfmoutpre:xzero?'))
    vscale = float(scope.query('wfmoutpre:ymult?'))
    voff = float(scope.query('wfmoutpre:yzero?'))
    vpos = float(scope.query('wfmoutpre:yoff?'))

    # Create scaled vectors for the time-domain plot
    total_time = tscale * record_length
    tstop = tstart + total_time
    scaled_time = np.linspace(tstart, tstop, num=record_length, endpoint=False)
    unscaled_wave = np.array(bin_wave, dtype='double')
    scaled_wave = (unscaled_wave - vpos) * vscale + voff

    waveforms[channel] = {
        'time': scaled_time,
        'wave': scaled_wave
    }

# Close the oscilloscope connection
scope.close()
rm.close()

# Calculate the total sine and total cosine


# Calculate the arctangent using the sine signal from CH2 and the cosine signal from CH3
if 'CH1' in waveforms and 'CH2' in waveforms and 'CH3' in waveforms and 'CH4' in waveforms:
    sine_wave = waveforms['CH1']['wave'] - waveforms['CH2']['wave']
    cosine_wave = waveforms['CH3']['wave'] - waveforms['CH4']['wave']
    
    # Ensure both arrays are of the same length for calculation
    min_length = min(len(sine_wave), len(cosine_wave))
    sine_wave = sine_wave[:min_length]
    cosine_wave = cosine_wave[:min_length]
    time_vector = waveforms['CH2']['time'][:min_length]
    
    arctangent_radians = np.arctan2(sine_wave, cosine_wave)
    arctangent_degrees = np.degrees(arctangent_radians)
    result = arctangent_degrees * factor
    print("Arctangent calculation completed and multiplied by factor.")

    # Plot the arctangent result
    plt.figure(figsize=(12, 6))
    plt.plot(time_vector, result)
    plt.title('Arctangent of CH2 (sine) and CH3 (cosine)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Result (pm)')
    plt.grid(True)
    plt.show()

    # Perform FFT on the arctangent result
    fft_result = np.fft.fft(result)
    fft_freq = np.fft.fftfreq(len(result), d=tscale)
    fft_magnitude = np.abs(fft_result) / len(result)

    # Plot the FFT of the arctangent result
    plt.figure(figsize=(12, 6))
    plt.plot(fft_freq[:len(result) // 2], fft_magnitude[:len(result) // 2])
    plt.title('FFT of Arctangent Result')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()

print("\nEnd of demonstration")