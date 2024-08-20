import os
import time
import base64
import struct
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import xml.etree.ElementTree as ET
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_newest_file(directory, extension=".xml"):
    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extension)]
        if not files:
            return None
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    except Exception as e:
        logging.error(f"Error finding the newest file: {e}")
        return None

def load_and_decode_waveform_data(xml_file_path):
    try:
        with open(xml_file_path, "rb") as file:
            tree = ET.parse(file)
            root = tree.getroot()
            ecg_leads_data = {}
            
            waveform_section = root.find('.//Waveform')
            if waveform_section:
                for lead_data in waveform_section.findall('LeadData'):
                    lead_id = lead_data.find('LeadID').text
                    wave_form_data_b64 = lead_data.find('WaveFormData').text
                    wave_form_data_bytes = base64.b64decode(wave_form_data_b64)
                    wave_form_data_decimals = [
                        struct.unpack('<H', wave_form_data_bytes[i:i+2])[0]
                        for i in range(0, len(wave_form_data_bytes), 2)
                    ]
                    ecg_leads_data[lead_id] = wave_form_data_decimals
            return ecg_leads_data
    except Exception as e:
        logging.error(f"Error loading or decoding XML: {e}")
        return {}

@app.get("/data")
async def get_data():
    base_directory = r'C:\sftp\sftpuser\sftpuser\F85C45669C94'
    current_date = datetime.now().strftime('%Y%m%d')
    target_directory = os.path.join(base_directory, current_date)
    newest_file = get_newest_file(target_directory)
    
    if newest_file:
        data = load_and_decode_waveform_data(newest_file)
        return JSONResponse(content=data)
    return JSONResponse(content={})

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/plot")
async def plot_signal(request: Request):
    return templates.TemplateResponse("plot_signal.html", {"request": request})