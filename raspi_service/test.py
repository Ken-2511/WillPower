#!/usr/bin/env python3

from picamera2 import Picamera2

picam2 = Picamera2()
capture_config = picam2.create_still_configuration()
picam2.start()

picam2.switch_mode_and_capture_file(capture_config, "photo.jpg")