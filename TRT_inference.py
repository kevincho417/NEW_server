import argparse
import sys
import time
from functools import partial

import numpy as np
import tritonclient.grpc as grpcclient
from tritonclient.utils import InferenceServerException
import time
# Define labels
label = ['F', 'N', 'Q', 'V']

# Argument parser setup
parser = argparse.ArgumentParser()
parser.add_argument(
    "-v", "--verbose", action="store_true", required=False, default=False, help="Enable verbose output"
)
parser.add_argument(
    "-u", "--url", type=str, required=False, default="192.168.50.214:8001", help="Inference server URL. Default is localhost:8001."
)
parser.add_argument(
    "-t", "--client-timeout", type=float, required=False, default=None, help="Client timeout in seconds. Default is None."
)

# Parse arguments
FLAGS = parser.parse_args()

# Create the Triton client
try:
    triton_client = grpcclient.InferenceServerClient(url=FLAGS.url, verbose=FLAGS.verbose)
except Exception as e:
    print("Context creation failed: " + str(e))
    sys.exit()

# Model name
model_name = "12_lead_ecg"

# Create inference inputs and outputs
inputs = []
outputs = []
pred_list = []
user_data = []
inputs.append(grpcclient.InferInput("input", [1, 12, 72], "FP32"))
outputs.append(grpcclient.InferRequestedOutput("output"))  # Adjust output name if needed

# Callback function for async inference
def callback(user_data, result, error):
    if error:
        user_data.append(error)
    else:
        user_data.append(result)

# CNN processing function
def CNN_processing(seg_list):
    
    for seg in seg_list:
        seg = np.float32(seg)
        seg = seg[None, :, :]  # Adjust input shape to [1, 12, 72]

        # Set data for inference
        inputs[0].set_data_from_numpy(seg)

        # Perform asynchronous inference
        triton_client.async_infer(
            model_name=model_name,
            inputs=inputs,
            callback=partial(callback, user_data),
            outputs=outputs,
            client_timeout=FLAGS.client_timeout
        )

    # Wait for results with a timeout
    time_out = 100
    while (len(user_data) == 0) and time_out > 0:
        time_out -= 1
        time.sleep(0.00000001)

    # Process results
    if len(user_data) >= 1:
        if isinstance(user_data[0], InferenceServerException):
            print(user_data[0])
            sys.exit(1)

        for ind in range(len(user_data)):
            output = user_data[ind].as_numpy("output")  # Adjust output name if needed
            pred = np.argmax(output)
            label_index = pred.item()
            pred_list.append(label[label_index])

    return pred_list

# Example usage
if __name__ == "__main__":
    example_seg_list = [np.random.rand(12, 72)]  # Replace with your actual input data
    start_time = time.time()
    for i in range (10000):
        predictions = CNN_processing(example_seg_list)
    end_time = time.time()
    test_time = end_time-start_time
    print(f"time:{test_time}")
