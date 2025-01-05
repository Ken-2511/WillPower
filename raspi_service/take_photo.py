#!/usr/bin/env python3

# filename: take_photo.py
# This file is for taking photos continuously in the background.

import os
import time
from picamera2 import Picamera2

picam2 = Picamera2()
capture_config = picam2.create_still_configuration()
picam2.start()

print("Camera started. Begin loop for taking photos.")

while True:
    try:
        filename = "temp_photo.jpg"

        # Sleep for a short time to calibrate the camera
        time.sleep(2)

        picam2.switch_mode_and_capture_file(capture_config, filename)

        # atomic rename to avoid reading and writing at the same time
        os.rename(filename, "photo.jpg")

        print("Photo taken.")

    except exception as e:
        print(f"Error: {e}")

    # Sleep for 20 seconds
    time.sleep(20)
