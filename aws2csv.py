import os
import csv
import IDS

def process_file(ids, filepath):
    # Open the file
    stream = ids.streaming.loadFile(filepath)
    print(f"Processing file: {filepath}")

    # Extract the base filename without extension
    base_filename = os.path.splitext(os.path.basename(filepath))[0]

    # Define the output CSV file path
    output_csv = os.path.join(os.path.dirname(filepath), f"{base_filename}.csv")

    # Save the data to a CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Assuming the first item in stream is the header
        header = stream[0] if stream else []
        if header:
            csvwriter.writerow(header)
            # Write the rest of the data
            for record in stream[1:]:
                csvwriter.writerow(record)
    print(f"Saved to: {output_csv}")

def main(folder_path):
    # Initialize the IDS device
    ids = IDS.Device("192.168.1.1")
    ids.connect()

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.aws'):
            filepath = os.path.join(folder_path, filename)
            process_file(ids, filepath)

if __name__ == '__main__':
    # Specify the folder path containing .aws files
    folder_path = r'C:\Users\ETH Lab\Desktop\Fabian\data_stream'
    main(folder_path)
