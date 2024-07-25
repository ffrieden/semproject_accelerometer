import time
import numpy as np
import matplotlib.pyplot as plt
import pyvisa
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

# Initialize VISA resource manager and list available instruments
rm = pyvisa.ResourceManager()
instruments = rm.list_resources()
print(f"Connected instruments: {instruments}")

# Define the function generator IP address
funcgen_ip = '192.168.1.4'  # Replace with the actual IP address
funcgen_name = f'TCPIP0::{funcgen_ip}::INSTR'

# Open the connection to the function generator
funcgen = rm.open_resource(funcgen_name)
funcgen.write_termination = '\n'
funcgen.read_termination = '\n'

funcgen.write('*CLS')



# Define the parameters
amplitude = 0.25  # volts
frequency = 20  # Hz
duration = 10  # seconds                         
channel_out = 1

funcgen.write(f'OUTPUT{channel_out}:STATE OFF')
time.sleep(1)
print('Output of function generator is turned off')

# Configure the function generator                      
funcgen.write(f'SOURCE{channel_out}:VOLTAGE:AMPLITUDE {amplitude}')
funcgen.write(f'SOURCE{channel_out}:FREQUENCY {frequency}')
funcgen.write(f'OUTPUT{channel_out}:STATE ON')

# Capture the waveform data
sample_rate_funcgen = 10000  # samples per second
total_samples = duration * sample_rate_funcgen
time_values = np.linspace(0, duration, total_samples)
waveform_values = amplitude * np.sin(2 * np.pi * frequency * time_values)

# Wait for the duration of the signal
print("Starting acquisition...")
time.sleep(duration)
print("Acquisition completed.")

# Turn off the output
funcgen.write(f'OUTPUT{channel_out}:STATE OFF')

# Perform FFT
fft_values = fft(waveform_values)
fft_freqs = fftfreq(total_samples, 1 / sample_rate_funcgen)

# Perform peak detection in FFT
peaks, _ = find_peaks(np.abs(fft_values)[:total_samples // 2], height=0)

# Print the found peaks in FFT
print("Found peaks in FFT at:")
for peak in peaks:
    print(f"Frequency: {fft_freqs[peak]:.2f} Hz, Amplitude: {np.abs(fft_values[peak]):.5f}")

# Plot the waveform
plt.figure(figsize=(10, 6))
plt.plot(time_values, waveform_values)
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.title('Waveform from Function Generator')
plt.grid(True)
plt.show()

# Plot the FFT with peaks
plt.figure(figsize=(10, 6))
plt.plot(fft_freqs[:total_samples // 2], np.abs(fft_values)[:total_samples // 2], label='FFT Amplitude')
plt.plot(fft_freqs[peaks], np.abs(fft_values)[peaks], "x", label='Peaks')
for peak in peaks:
    plt.annotate(f'{np.abs(fft_values[peak]):.3f}',
                 (fft_freqs[peak], np.abs(fft_values[peak])),
                 textcoords="offset points", xytext=(0,10), ha='center')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('FFT of Waveform')
plt.legend()
plt.grid(True)
plt.show()

# Close the connection to the function generator
funcgen.close()