from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import time
from datetime import datetime
import xml.etree.ElementTree as ET
import base64
import struct

app = FastAPI()

# Directory where HTML, JS, CSS files are stored
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static")

# Your existing functions here
def get_second_newest_file(directory, seconds=2):
    current_time = time.time()
    files_with_times = []

    # Iterate through files in the directory
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(file_path):
            # Get the modification time of the file
            file_mod_time = os.path.getmtime(file_path)
            
            # If the file was modified within the last 'seconds' seconds
            if current_time - file_mod_time <= seconds:
                files_with_times.append((file_path, file_mod_time))

    # Sort the list by modification time in descending order and pick the second newest
    files_with_times.sort(key=lambda x: x[1], reverse=True)
    return files_with_times[1][0] if len(files_with_times) > 1 else None

def load_and_decode_waveform_data(xml_file_path):
    try:
        # Load and parse the XML file
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Dictionary to store decoded WaveFormData for each lead
        ecg_leads_data = {}

        # Navigate to the Waveform section
        waveform_section = root.find('.//Waveform')
        if waveform_section is not None:
            # Iterate over each LeadData element
            for lead_data in waveform_section.findall('LeadData'):
                lead_id = lead_data.find('LeadID').text
                wave_form_data_b64 = lead_data.find('WaveFormData').text

                # Decode Base64 to bytes
                wave_form_data_bytes = base64.b64decode(wave_form_data_b64)

                # Convert bytes to 16-bit decimal values (assuming little-endian byte order)
                wave_form_data_decimals = [struct.unpack('<H', wave_form_data_bytes[i:i+2])[0] for i in range(0, len(wave_form_data_bytes), 2)]

                # Store the decimal values for each lead
                ecg_leads_data[lead_id] = wave_form_data_decimals

        return ecg_leads_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ecg-data")
async def get_ecg_data():
    base_directory = r'C:\sftp\sftpuser\sftpuser\F85C45669C94'
    current_date = datetime.now().strftime('%Y%m%d')
    target_directory = os.path.join(base_directory, current_date)
    second_newest_file = get_second_newest_file(target_directory, seconds=6)
    if second_newest_file:
        data = load_and_decode_waveform_data(second_newest_file)
        return {"data": data}
    raise HTTPException(status_code=404, detail="No new file found")

