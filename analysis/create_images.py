# this file is for creating the images from a specific day
# three images to be created:
# 1. the photo taken by the raspberry pi camera, filename: "hh-mm-ss.jpg"
# 2. the screenshot on the laptop screen, filename: "hh-mm-ss_____DISPLAY1.bmp"
# 3. the screenshot on the main screen, filename: "hh-mm-ss_____DISPLAY2.bmp"

import os
import cv2
import numpy as np

from config import PHOTOS_PATH, SCREENSHOTS_PATH, DATE, OUTPUT_PATH


# load three images from the timestamp as numpy array
def load_image(timestamp: str):
    # load the photo taken by the raspberry pi camera
    photo = cv2.imread(os.path.join(PHOTOS_PATH, DATE, timestamp + ".jpg"))
    # load the screenshot on the laptop screen
    display1 = cv2.imread(os.path.join(SCREENSHOTS_PATH, DATE, timestamp + "_____DISPLAY1.bmp"))
    # load the screenshot on the main screen
    display2 = cv2.imread(os.path.join(SCREENSHOTS_PATH, DATE, timestamp + "_____DISPLAY2.bmp"))
    return photo, display1, display2


def save_images(date: str, photo: np.ndarray, display1: np.ndarray, display2: np.ndarray):
    # save the photo taken by the raspberry pi camera
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + ".jpg"), photo)
    # save the screenshot on the laptop screen
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + "_____DISPLAY1.bmp"), display1)
    # save the screenshot on the main screen
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + "_____DISPLAY2.bmp"), display2)


# get the timestamps that we have all the three images
def get_timestamps():
    # list all the files in the photos path
    photos = os.listdir(os.path.join(PHOTOS_PATH, DATE))
    # list all the files in the screenshots path
    screenshots = os.listdir(os.path.join(SCREENSHOTS_PATH, DATE))
    # get the timestamps that we have all the three images
    timestamps_camera = set()
    timestamps_display1 = set()
    timestamps_display2 = set()
    for photo in photos:
        # get the timestamp from the photo
        timestamp = photo.split(".")[0]
        timestamps_camera.add(timestamp)
    for screenshot in screenshots:
        # get the timestamp from the screenshot
        timestamp = screenshot.split("_____")[0]
        if "DISPLAY1" in screenshot:
            timestamps_display1.add(timestamp)
        else:
            timestamps_display2.add(timestamp)
    # get the timestamps that we have all the three images
    timestamps = timestamps_camera.intersection(timestamps_display1).intersection(timestamps_display2)
    # convert to list and sort
    timestamps = list(timestamps)
    timestamps.sort()
    return timestamps


def mix_images(real_time_output=False):
    timestamps = get_timestamps()
    # create the images
    if real_time_output:
        print("Creating images...")
    images = load_image(timestamps[0])
    camera_img = np.zeros_like(images[0], dtype=np.float64)
    display1_img = np.zeros_like(images[1], dtype=np.float64)
    display2_img = np.zeros_like(images[2], dtype=np.float64)
    # add all the images
    for timestamp in timestamps:
        if real_time_output:
            print(timestamp)
        images = load_image(timestamp)
        camera_img += images[0].astype(np.float64)
        display1_img += images[1].astype(np.float64)
        display2_img += images[2].astype(np.float64)
    # restrict the value from 0 to 255
    if real_time_output:
        print("Normalizing the images...")
    camera_img -= camera_img.min()
    camera_img /= camera_img.max()
    camera_img *= 255
    display1_img -= display1_img.min()
    display1_img /= display1_img.max()
    display1_img *= 255
    display2_img -= display2_img.min()
    display2_img /= display2_img.max()
    display2_img *= 255
    # convert to uint8
    camera_img = camera_img.astype(np.uint8)
    display1_img = display1_img.astype(np.uint8)
    display2_img = display2_img.astype(np.uint8)
    # save the images
    save_images(DATE, camera_img, display1_img, display2_img)
    if real_time_output:
        print("Images created successfully")


if __name__ == '__main__':
    mix_images(True)
