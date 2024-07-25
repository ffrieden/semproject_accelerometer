import time
import numpy as np
import matplotlib.pyplot as plt
import pyvisa
from scipy.signal import find_peaks, butter, filtfilt

# Initialize VISA resource manager and list available instruments
rm = pyvisa.ResourceManager()
instruments = rm.list_resources()
print(f"Connected instruments: {instruments}")

# Define the function generator IP address
funcgen_ip = '192.168.1.4'
funcgen_name = f'TCPIP0::{funcgen_ip}::INSTR'
# Open the connection to the function generator
funcgen = rm.open_resource(funcgen_name)
funcgen.write_termination = '\n'
funcgen.read_termination = '\n'

# Open the connection to the oscilloscope
oscilloscope_ip = '192.168.1.10'
scope_name = f'TCPIP0::{oscilloscope_ip}::INSTR'
scope = rm.open_resource(scope_name)
scope.timeout = 100000  # Increase timeout to 100 seconds
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls')
channels = ['CH1', 'CH2', 'CH3', 'CH4']
print(scope.query('*idn?'))

# Define settings for each channel
channel_settings = {
    'CH1': {'sampling_rate': 1e5, 'v_div': 0.1},  # sin +
    'CH2': {'sampling_rate': 1e5, 'v_div': 0.1},  # sin -
    'CH3': {'sampling_rate': 1e5, 'v_div': 0.1},  # cos +
    'CH4': {'sampling_rate': 1e5, 'v_div': 0.1}   # cos -
}
desired_time_window = 11  # seconds

# Define the multiplication factor for the arctangent
factor = 100000 / 90  # pm/degree

# Define the initial parameters for the function generator
initial_amplitude = 0.05  # Initial amplitude in volts (pp is the same)
max_amplitude = 1  # Maximum amplitude in volts
amplitude_increment = 0.05  # Increment in volts
initial_frequency = 20  # Initial frequency in Hz
max_frequency = 300  # Maximum frequency in Hz
frequency_increment = 20  # Frequency increment in Hz
channel_out = 1

# Reset the oscilloscope and configure horizontal settings
scope.write('*rst')
scope.write('header 0')
scope.query('*opc?')

# Turn on Channels and configure settings of oscilloscope
for channel, settings in channel_settings.items():
    scope.write(f'SELect:{channel} ON')
    scope.write(f':{channel}:SCAle {settings["v_div"]}')  # V/div
    scope.write(f':{channel}:COUP AC')  # AC or DC
    scope.write(f'{channel}:PROBEFunc:EXTAtten 1')  # 1x or 10x
scope.write('acquire:mode HIRES')

# Configure horizontal settings for each channel
for channel, settings in channel_settings.items():
    scope.write('HORIZONTAL:MODE MANUAL')
    sampling_rate = settings['sampling_rate']
    record_length = int(sampling_rate * desired_time_window)
    scope.write(f'HORIZONTAL:MODE:SAMPLERATE {sampling_rate}')
    scope.write(f'HORIZONTAL:RECORDLENGTH {record_length}')

scope.query('*opc?')

# Configure data and acquisition settings
scope.write('data:encdg SRIBINARY')
scope.write('data:start 1')
scope.write(f'data:stop {record_length}')
scope.write('wfmoutpre:byt_n 1')

scope.write('acquire:state 0')
scope.write('acquire:stopafter SEQUENCE')

# Function to acquire waveform data
def acquire_waveform(scope, channel, settings):
    scope.write(f'data:source {channel}')
    time.sleep(0.1)  # Short delay
    current_source = scope.query('DATA:SOURCE?').strip()
    print(f"Current data source set to: {current_source}")

    record_length = int(settings['sampling_rate'] * desired_time_window)
    scope.write(f'data:stop {record_length}')

    bin_wave = scope.query_binary_values('curve?', datatype='b', container=np.array)

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

    return scaled_time, scaled_wave, tscale


# Loop over amplitude range and perform measurements
for amplitude in np.arange(initial_amplitude, max_amplitude + amplitude_increment, amplitude_increment):
    for frequency in np.arange(initial_frequency, max_frequency + frequency_increment, frequency_increment):
        # Configure the function generator
        funcgen.write(f'SOURCE{channel_out}:FUNCTION SIN')
        funcgen.write(f'SOURCE{channel_out}:VOLTAGE:AMPLITUDE {amplitude}')
        funcgen.write(f'SOURCE{channel_out}:FREQUENCY {frequency}')
        funcgen.write(f'OUTPUT{channel_out}:STATE ON')
        time.sleep(1)
        print('Output of function generator is turned on')
        print(f"Starting acquisition for amplitude: {amplitude} V and frequency: {frequency} Hz...")

        # Start acquisition
        scope.write('acquire:state 1')
        scope.query('*opc?')

        waveforms = {}

        # Transfer waveform data from the oscilloscope for each channel
        for channel, settings in channel_settings.items():
            scaled_time, scaled_wave, tscale = acquire_waveform(scope, channel, settings)
            waveforms[channel] = {
                'time': scaled_time,
                'wave': scaled_wave,
                'tscale': tscale
            }

        # Turn off the output
        funcgen.write(f'OUTPUT{channel_out}:STATE OFF')
        time.sleep(1)
        print('Output of function generator is turned off')

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
            plt.title(f'Arctangent IDS for {amplitude}V and {frequency}Hz')
            plt.xlabel('Time (seconds)')
            plt.ylabel('Result (pm)')
            plt.grid(True)
            # plt.show()

            # Perform FFT on the arctangent result
            fft_result = np.fft.fft(result)
            fft_freq = np.fft.fftfreq(len(result), d=tscale)
            fft_magnitude = np.abs(fft_result) / len(result)  # normalization

            # Detect peaks in the FFT magnitude
            peak_height_threshold = 0.01 * np.max(fft_magnitude)  # Dynamic threshold based on max magnitude
            peak_distance_threshold = 100000  # Minimum number of samples between peaks
            peak_prominence_threshold = 1000  # Adjust this value based on your data

            peaks, properties = find_peaks(
                fft_magnitude[:len(result) // 2],
                height=peak_height_threshold,
                distance=peak_distance_threshold,
                prominence=peak_prominence_threshold
                   # Plot the FFT of the arctangent result
            )
            plt.figure(figsize=(12, 6))
            plt.plot(fft_freq[:len(result) // 2], fft_magnitude[:len(result) // 2])
            plt.title(f'FFT IDS for {amplitude}V and {frequency}Hz')
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Magnitude')
            plt.grid(True)
            # plt.show()

            # Print detected peak frequencies and their magnitudes
            for peak in peaks:
                print(f"Peak detected at frequency: {fft_freq[peak]} Hz with magnitude: {fft_magnitude[peak]}")

            # Open or create the results file in append mode
            with open('output_1peak.txt', 'a') as file:
                if len(peaks) > 0:
                    # Get the magnitude and frequency of the first detected peak
                    first_peak_magnitude = fft_magnitude[peaks[0]]
                    first_peak_frequency = fft_freq[peaks[0]]
                else:
                    # If no peaks are detected, set values to None or some default
                    first_peak_magnitude = None
                    first_peak_frequency = None

                print(f"Writing results: {amplitude} V, {frequency} Hz, {first_peak_frequency} Hz, {first_peak_magnitude}")

                # Write the results to the file
                file.write(f'{amplitude} V, {frequency} Hz, {first_peak_frequency} Hz, {first_peak_magnitude}\n')

            print("\nResults saved to output_1peak.txt")
funcgen.close()
scope.close()
rm.close()