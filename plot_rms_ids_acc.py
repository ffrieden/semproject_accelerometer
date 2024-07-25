import matplotlib.pyplot as plt
import pandas as pd

# Read the data from the file
file_path = 'output_rms_wStd_2.txt'

# Read the data into a pandas DataFrame
df = pd.read_csv(file_path, header=None, names=['Frequency', 'rms_ids_mean', 'rms_ids_std', 'rms_acc_mean', 'rms_acc_std'])

# Convert the Frequency to numeric, stripping out ' Hz'
df['Frequency'] = df['Frequency'].str.replace(' Hz', '').astype(int)

# Plot 1: Mean RMS IDs Acceleration with Error Bars
df_ids = df[['Frequency', 'rms_ids_mean', 'rms_ids_std']]
grouped_ids = df_ids.groupby('Frequency').mean().reset_index()

plt.figure(figsize=(10, 6))
plt.errorbar(grouped_ids['Frequency'], grouped_ids['rms_ids_mean'], 
             yerr=grouped_ids['rms_ids_std'], fmt='o', capsize=5)
plt.xticks(grouped_ids['Frequency'])
plt.xlabel('Frequency (Hz)')
plt.ylabel('RMS acceleration (m/s²)')
plt.title('RMS acceleration (IDS)')
plt.grid(True)
#plt.show()

# Plot 2: Mean RMS ACC Acceleration with Error Bars
df_acc = df[['Frequency', 'rms_acc_mean', 'rms_acc_std']]
grouped_acc = df_acc.groupby('Frequency').mean().reset_index()

plt.figure(figsize=(10, 6))
plt.errorbar(grouped_acc['Frequency'], grouped_acc['rms_acc_mean'], 
             yerr=grouped_acc['rms_acc_std'], fmt='o', capsize=5)
plt.xticks(grouped_acc['Frequency'])
plt.xlabel('Frequency (Hz)')
plt.ylabel('RMS acceleration (m/s²)')
plt.title('RMS acceleration (ACC)')
plt.grid(True)
plt.show()