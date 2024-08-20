import os
import time
from datetime import datetime
from threading import Thread
from read_xml import load_and_decode_waveform_data
buffer = {f"Lead{i+1}": [] for i in range(12)}  # Initialize a buffer for each of the 12 leads

def get_newest_file(directory, buffer_duration=1):
    while True:
        current_time = time.time()
        newest_file = None
        newest_time = None

        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            try:
                if os.path.isfile(file_path):
                    file_mod_time = os.path.getmtime(file_path)
                    if current_time - file_mod_time <= buffer_duration:
                        if newest_time is None or file_mod_time > newest_time:
                            newest_time = file_mod_time
                            newest_file = file_path
            except PermissionError:
                print(f"Permission denied: {file_path}")
            except Exception as e:
                print(f"Error accessing file {file_path}: {e}")

        if newest_file:
            process_file(newest_file)
        time.sleep(1)

def process_file(file_path):
    # Process the file and update the buffer
    ecg_data = load_and_decode_waveform_data(file_path)  # Assuming this function is already implemented
    for lead, data in ecg_data.items():
        buffer[lead] = data
    print(buffer)

def start_file_monitoring(directory):
    thread = Thread(target=get_newest_file, args=(directory,))
    thread.daemon = True
    thread.start()
