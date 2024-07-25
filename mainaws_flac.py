import time
import numpy as np
import pyvisa
import IDS
import os
import sounddevice as sd
import soundfile as sf
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
#print(script_dir)

def list_devices():
    print("Available audio devices:")
    devices = sd.query_devices()
    for index, device in enumerate(devices):
        print(f"{index}: {device['name']} ({'input' if device['max_input_channels'] > 0 else 'output'})")

def main():
    # Initialize VISA resource manager and list available instruments
    rm = pyvisa.ResourceManager()
    instruments = rm.list_resources()
    print(f"Connected instruments: {instruments}")

    # Configure the function generator 
    funcgen_ip = '192.168.1.4'
    funcgen_name = f'TCPIP0::{funcgen_ip}::INSTR'
    funcgen = rm.open_resource(funcgen_name)
    funcgen.write_termination = '\n'
    funcgen.read_termination = '\n'
    funcgen.write('*CLS')
    
    # Configure the IDS
    ids = IDS.Device("192.168.1.1")
    ids.connect()

    # Setting up audio device
    device_id = 1
    #duration = 20
    sample_rate = 44100

    if device_id is None:
        device_id = sd.default.device['input']
    else:
        sd.default.device = device_id

    device_info = sd.query_devices(device_id)
    device_name = device_info['name']
    print(f"Using device: {device_name}")

    try:
        print("Warm-up recording...")
        warmup_audio = sd.rec(int(5 * sample_rate), samplerate=sample_rate, channels=2, dtype='float32')
        sd.wait()  # Wait until warm-up recording is finished
        print("Warm-up finished.")
    except Exception as e:
        print(f"Warm-up recording failed: {e}")
        return

    # Define the initial parameters for the function generator
    initial_amplitude = 0.8  # Initial amplitude in volts (pp is the same)
    max_amplitude = 1  # Maximum amplitude in volts
    amplitude_increment = 0.05 # Increment in volts
    initial_frequency = 20  # Initial frequency in Hz
    max_frequency = 300  # Maximum frequency in Hz
    frequency_increment = 20  # Frequency increment in Hz
    channel_out = 1

    for amplitude in np.arange(initial_amplitude, max_amplitude + amplitude_increment, amplitude_increment):
        for frequency in np.arange(initial_frequency, max_frequency + frequency_increment, frequency_increment):
            # Configure the function generator
            funcgen.write(f'SOURCE{channel_out}:FUNCTION SIN')
            funcgen.write(f'SOURCE{channel_out}:VOLTAGE:AMPLITUDE {amplitude}')
            funcgen.write(f'SOURCE{channel_out}:FREQUENCY {frequency}')
            funcgen.write(f'OUTPUT{channel_out}:STATE ON')
            time.sleep(2)
            print('Output of function generator is turned on')
            print(f"Starting acquisition for amplitude: {amplitude} V and frequency: {frequency} Hz...")
            
            # Round amplitude and frequency to two decimal places for file name
            rounded_amplitude = round(amplitude, 2)
            rounded_frequency = round(frequency, 2)

            # Construct the absolute path for the data file
            data_file = os.path.join(script_dir, f"data_{rounded_amplitude}_{rounded_frequency}.aws")

            # Open a stream for axis0
            stream = ids.streaming.open(True, 10, data_file, axis0=True)
            print(stream)
            
            # Start background streaming
            ids.streaming.startBackgroundStreaming(True, 10, data_file, axis0=True)
            print("Background streaming started")

            # Main recording
            print("Main recording...")
            audio = sd.rec(int(10 * sample_rate), samplerate=sample_rate, channels=2, dtype='float32')
            sd.wait()  # Wait until main recording is finished
            
            time.sleep(1)

            # Stop the background stream
            ids.streaming.stopBackgroundStreaming()
            print(f"Background streaming stopped, data for {rounded_amplitude}V and {rounded_frequency}Hz saved to .aws file")
            print("Recording finished.")

            # Generate filename 
            audio_file = os.path.join(script_dir, f"data_{rounded_amplitude}_{rounded_frequency}.flac")

            # Save the recorded audio
            sf.write(audio_file, audio, sample_rate)
            print(f"File saved as data_{rounded_amplitude}_{rounded_frequency}.flac")

            # Turn off the output
            funcgen.write(f'OUTPUT{channel_out}:STATE OFF')
            time.sleep(2)
            print('Output of function generator is turned off')

    print("\nEnd")

    funcgen.close()
    rm.close()

if __name__ == '__main__':
    main()