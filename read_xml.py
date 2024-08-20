import xml.etree.ElementTree as ET
import base64
import struct
import matplotlib.pyplot as plt

def load_and_decode_waveform_data(xml_file_path):
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
if __name__ =="__main__":
    # Replace 'path_to_your_xml_file.xml' with the actual path to your XML file
    xml_file_path = 'Z999999999_2024-08-20-13-56-04_SN_4.xml'
    ecg_waveform_data = load_and_decode_waveform_data(xml_file_path)

    # Print and plot the decimal values for Lead I
    for lead_id, data in ecg_waveform_data.items():
        if lead_id == "I":
            print(f"Lead {lead_id}: {data}")
            print(len(data))
            plt.figure(figsize=(10, 4))  # Set the figure size
            plt.plot(data, label='Lead I', linestyle='-', color='b')  # Plot Lead I data
            plt.title('ECG Waveform for Lead I')  # Title of the plot
            plt.xlabel('Sample Number')  # X-axis label
            plt.ylabel('Amplitude')  # Y-axis label
            plt.grid(True)  # Enable grid for easier visualization
            plt.legend()  # Show legend
            plt.show()
