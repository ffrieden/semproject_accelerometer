# README for Semester Project Scripts at the Fundamental Interactions Group, ETHZ

## Remotely Control an Oscilloscope and a Function Generator

This directory contains several scripts designed to remotely control an oscilloscope and a function generator. Below is a brief description of each script:

### 1. `funcgen.py`
This script remotely controls an arbitrary function generator (AFG31000, Tektronix). It requires the IP address, channel to control, amplitude, and frequency as input parameters. The script generates the waveform and performs an FFT.

### 2. `scope.py`
This script remotely controls an oscilloscope (MSO24 Mixed Signal Oscilloscope, Tektronix). It requires the IP address and the input channel. Lines 42 and 43 allow you to change the input settings to either AC or DC and the attenuation to either 1x or 10x. The waveform and its FFT are plotted.

### 3. `resetscope.py`
This script is used to reset the oscilloscope to factory settings, useful in case of connection issues.

### 4. `idstrace_simul.py`
This script is designed for the output of the IDS, requiring 4 channels for one axis monitored simultaneously by the oscilloscope.

### 5. `maincalibration_funcgen_scope.py`
This script performs automated measurements using a function generator and an oscilloscope. It combines the functionalities of `funcgen.py` and `scope.py`. It controls these instruments via the VISA interface, sweeping through a range of amplitudes and frequencies for the function generator and capturing waveform data from the oscilloscope. Specific to the IDS, the script performs arctangent calculations on the acquired data, FFT analysis, and peak detection.

### 6. `colorplot.py`
These scripts create different color plots from the `output.txt` files.

## Remotely Control the Streaming of an IDS

In this directory, there is a subdirectory called `data_stream` containing Python files to control an IDS (IDS3010 attocube). To use the streaming function of the IDS, the `streaming` subdirectory is necessary, which includes the DLL and various Python files (streaming is only possible on Windows). The following files are used for measurements with the accelerometer:

### 1. `mainaws.py`
This script automates the configuration and operation of a function generator and IDS device for simultaneous data acquisition. It initializes the devices, configures the function generator to output a sine wave with varying amplitude and frequency, and collects data using the IDS device's streaming function. The collected data is saved in `.aws` files.

### 2. `mainaws_flac.py`
This script automates the configuration and operation of a function generator, IDS device, and an audio recording device (an accelerometer in this case) for comprehensive data acquisition. It initializes the devices, configures the function generator to output a sine wave with varying amplitude and frequency, collects data using the IDS device (streaming function) and saves it to a `.aws` file, and records the displacement data of the accelerometer, saving it to a `.flac` file.

### 3. `aws2csv.py`
This script processes all `.aws` files into `.csv` files in the desired directory.

### 4. `process_csv_flac.py`
This script processes and analyzes displacement data from `.csv` files and audio data from `.flac` files. It performs various tasks, including filtering, FFT analysis, acceleration calculation, and RMS calculation. The results are saved to text files for further analysis (needs to be in the same directory as the data files).

---

Please ensure that you have all the necessary dependencies installed and properly configured to use these scripts effectively.