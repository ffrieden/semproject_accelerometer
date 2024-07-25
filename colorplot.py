import numpy as np
import matplotlib.pyplot as plt

# Initialize lists to store the data
amplitudes = []
frequencies = []
peak_frequencies = []
peak_magnitudes = []

# Read the data from the file
with open('output_idspeak.txt', 'r') as file:
    for line in file:
        amplitude, frequency, first_peak_frequency, first_peak_magnitude = line.strip().split(', ')
        amplitudes.append(float(amplitude.split()[0]))
        frequencies.append(float(frequency.split()[0]))
        peak_frequencies.append(float(first_peak_frequency.split()[0]))
        peak_magnitudes.append(float(first_peak_magnitude))

# Convert lists to numpy arrays for easier manipulation
amplitudes = np.array(amplitudes)
frequencies = np.array(frequencies)
peak_frequencies = np.array(peak_frequencies)
peak_magnitudes = np.array(peak_magnitudes)

# Create a 2D grid of the data
amplitude_unique = np.unique(amplitudes)
frequency_unique = np.unique(frequencies)

# Adjust the grid to only include the measured data
amplitude_edges = amplitude_unique - np.diff(amplitude_unique, prepend=0)/2
amplitude_edges = np.append(amplitude_edges, amplitude_unique[-1] + np.diff(amplitude_unique)[-1]/2)
frequency_edges = frequency_unique - np.diff(frequency_unique, prepend=0)/2
frequency_edges = np.append(frequency_edges, frequency_unique[-1] + np.diff(frequency_unique)[-1]/2)

# Create the grid for peak magnitudes
peak_magnitude_grid = np.zeros((len(frequency_unique), len(amplitude_unique)))

for i, amp in enumerate(amplitude_unique):
    for j, freq in enumerate(frequency_unique):
        mask = (amplitudes == amp) & (frequencies == freq)
        if mask.any():
            peak_magnitude_grid[j, i] = peak_magnitudes[mask][0]

# Set the magnitude level of zero to white
cmap = plt.get_cmap('viridis')
cmap.set_under(color='white')

# Create the color plot with centered blocks and black frame
plt.figure(figsize=(10, 6))
plt.pcolormesh(amplitude_edges, frequency_edges, peak_magnitude_grid, shading='auto', cmap=cmap, edgecolor='black', linewidth=0.2, vmin=0.01)
plt.colorbar(label='First Peak Magnitude')

# Adjust tick positions and labels
plt.xticks(amplitude_unique)
plt.yticks(frequency_unique)

plt.xlabel('Amplitude (V)')
plt.ylabel('Frequency (Hz)')
plt.title('Color Plot of First Peak Magnitudes')
plt.grid(True)
plt.show()