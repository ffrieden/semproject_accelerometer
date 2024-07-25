import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.signal import find_peaks
import time

def main():

    # Define the initial parameters for the function generator
    initial_amplitude = 0.05 # Initial amplitude in volts (pp is the same)
    max_amplitude = 1  # Maximum amplitude in volts
    amplitude_increment = 0.05  # Increment in volts
    initial_frequency = 20  # Initial frequency in Hz
    max_frequency = 300  # Maximum frequency in Hz
    frequency_increment = 20  # Frequency increment in Hz

    script_dir = os.path.dirname(os.path.abspath(__file__))

    for amplitude in np.arange(initial_amplitude, max_amplitude + amplitude_increment, amplitude_increment):
        for frequency in np.arange(initial_frequency, max_frequency + frequency_increment, frequency_increment):
            
            # Round amplitude and frequency to two decimal places for file name
            rounded_amplitude = round(amplitude, 2)
            rounded_frequency = round(frequency, 2)
            
            #file_path = f'data_{amplitude}_{frequency}.csv'
            file_name = f'data_{rounded_amplitude}_{rounded_frequency}.csv'
            file_path = os.path.join(script_dir, file_name)
            
            if not os.path.isfile(file_path):
                print(f"File not found: {file_path}")
                continue
            
            # Read the file
            data = pd.read_csv(file_path, header=None, names=['Time', 'Pos0', 'Unused1', 'Unused2'], usecols=['Time', 'Pos0'])

            # Calculate the mean of the 'Pos0' column
            mean_position = data['Pos0'].mean()
            print(f"The mean of the absolute positions ({rounded_amplitude}V_{rounded_frequency}Hz) is: {mean_position}")
            # Plot
            trace = data['Displacement'] = data['Pos0'] - mean_position
            tscale = data['Time']

            plt.figure(figsize=(10, 6))
            plt.plot(tscale, trace, label='Displacement')
            plt.xlabel('Time (s)')
            plt.ylabel('Displacement (pm)')
            plt.title('Displacement vs Time')
            plt.grid(True)
            #plt.show()

            # Perform FFT
            fft_result = np.fft.fft(data['Displacement'])
            fft_result[:100] = 0
            fft_freq = np.fft.fftfreq(len(fft_result), d=(data['Time'][1] - data['Time'][0]))
            fft_magnitude = np.abs(fft_result) / len(trace)

            peak_height_threshold = 0.01 * np.max(fft_magnitude)  # Dynamic threshold based on max magnitude
            peak_distance_threshold = 50  # Minimum number of samples between peaks
            peak_prominence_threshold = 10  # Adjust this value based on your data

            peaks, properties = find_peaks(
                fft_magnitude[:len(trace) // 2],
                height=peak_height_threshold,
                distance=peak_distance_threshold,
                prominence=peak_prominence_threshold
            )

            # Plot FFT
            plt.figure(figsize=(10, 6))
            plt.plot(fft_freq[:len(fft_freq)//2], np.abs(fft_result)[:len(fft_freq)//2])
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Amplitude')
            plt.title('FFT of Displacement')
            plt.xlim(0, 1000)
            plt.grid(True)
            #plt.show()

            for peak in peaks:
                print(f"Peak detected at frequency: {fft_freq[peak]} Hz with magnitude: {fft_magnitude[peak]}")

            # Open or create the second results file in append mode
            with open('output_ids_peakratio_1.txt', 'a') as file:
                if len(peaks) > 0:
                    # Get the magnitudes and frequencies of the first and second detected peaks
                    first_peak_magnitude = fft_magnitude[peaks[0]]
                    first_peak_frequency = fft_freq[peaks[0]]
                    if len(peaks) > 1:
                        second_peak_magnitude = fft_magnitude[peaks[1]]
                        second_peak_frequency = fft_freq[peaks[1]]
                    else:
                        second_peak_magnitude = None
                        second_peak_frequency = None
                else:
                    # If no peaks are detected, set values to None or some default
                    first_peak_magnitude = None
                    first_peak_frequency = None
                    second_peak_magnitude = None
                    second_peak_frequency = None

                # Calculate the ratio of the first peak magnitude to the second peak magnitude
                if first_peak_magnitude is not None and second_peak_magnitude is not None:
                    peak_ratio = first_peak_magnitude / second_peak_magnitude
                else:
                    peak_ratio = 0

                print(f"Writing results: {rounded_amplitude} V, {rounded_frequency} Hz, {first_peak_frequency} Hz, {first_peak_magnitude}, {second_peak_frequency} Hz, {second_peak_magnitude}, {peak_ratio}")

                # Write the results to the file
                #file.write(f'{amplitude} V, {frequency} Hz, {first_peak_frequency} Hz, {first_peak_magnitude}, {second_peak_frequency} Hz, {second_peak_magnitude}, {peak_ratio}\n')
                
                file.write(f'{rounded_amplitude} V, {rounded_frequency} Hz, {peak_ratio}\n')
                print("\nPeak ratio results saved to output_ids_peakratio_1.txt")
            with open('output_ids_firstpeak_1.txt', 'a') as file:
                file.write(f'{rounded_amplitude} V, {rounded_frequency} Hz, {first_peak_magnitude}\n')
                print("\nFirst peak magnitude results saved to output_ids_firstpeak_1.txt")

    print("\nEnd")


if __name__ == '__main__':
    main()