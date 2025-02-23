import os
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from analysis.config import PHOTOS_PATH, SCREENSHOTS_PATH, DATE, OUTPUT_PATH


def preload_images(real_time_output=False):
    """
    Preload all images into memory for faster processing.
    """
    timestamps = get_timestamps()
    images = {}
    for timestamp in timestamps:
        if real_time_output:
            print(f"Preloading {timestamp}...")
        photo = cv2.imread(os.path.join(PHOTOS_PATH, DATE, timestamp + ".jpg"))
        display1 = cv2.imread(os.path.join(SCREENSHOTS_PATH, DATE, timestamp + "_____DISPLAY1.bmp"))
        display2 = cv2.imread(os.path.join(SCREENSHOTS_PATH, DATE, timestamp + "_____DISPLAY2.bmp"))
        images[timestamp] = (photo, display1, display2)
    return images


def save_images(date: str, photo: np.ndarray, display1: np.ndarray, display2: np.ndarray):
    """
    Save the processed images to the output directory.
    """
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + ".jpg"), photo)
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + "_____DISPLAY1.bmp"), display1)
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + "_____DISPLAY2.bmp"), display2)


def get_timestamps():
    """
    Get all timestamps that have corresponding images for camera and displays.
    """
    photos = os.listdir(os.path.join(PHOTOS_PATH, DATE))
    screenshots = os.listdir(os.path.join(SCREENSHOTS_PATH, DATE))

    timestamps_camera = {photo.split(".")[0] for photo in photos}
    timestamps_display1 = {screenshot.split("_____")[0] for screenshot in screenshots if "DISPLAY1" in screenshot}
    timestamps_display2 = {screenshot.split("_____")[0] for screenshot in screenshots if "DISPLAY2" in screenshot}

    timestamps = timestamps_camera.intersection(timestamps_display1).intersection(timestamps_display2)
    return sorted(timestamps)


def normalize_image(image):
    """
    Normalize an image to the range [0, 255] and convert to uint8.
    """
    image -= np.min(image)
    image /= np.ptp(image)  # Peak-to-peak range (max - min)
    image *= 255
    return image.astype(np.uint8)


def add_images(timestamps, preloaded_images, results, real_time_output=False):
    """
    Add images in the given timestamp range to the accumulator.
    """
    for timestamp in timestamps:
        if real_time_output:
            print(f"Processing {timestamp}...")
        images = preloaded_images[timestamp]
        results[0] += images[0].astype(np.float64)
        results[1] += images[1].astype(np.float64)
        results[2] += images[2].astype(np.float64)


def mix_images(real_time_output=False):
    """
    Main function to mix images and save the output.
    """
    preloaded_images = preload_images(real_time_output)
    timestamps = list(preloaded_images.keys())

    # Initialize accumulators for camera and display images
    camera_img = np.zeros_like(next(iter(preloaded_images.values()))[0], dtype=np.float64)
    display1_img = np.zeros_like(next(iter(preloaded_images.values()))[1], dtype=np.float64)
    display2_img = np.zeros_like(next(iter(preloaded_images.values()))[2], dtype=np.float64)

    results = [camera_img, display1_img, display2_img]

    # Split timestamps for parallel processing
    num_workers = 4
    split_timestamps = np.array_split(timestamps, num_workers)

    if real_time_output:
        print("Starting parallel processing...")

    # Process images in parallel
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(add_images, split_timestamps, [preloaded_images] * num_workers, [results] * num_workers, [real_time_output] * num_workers)

    if real_time_output:
        print("Normalizing images...")

    # Normalize and save images
    camera_img = normalize_image(results[0])
    display1_img = normalize_image(results[1])
    display2_img = normalize_image(results[2])

    save_images(DATE, camera_img, display1_img, display2_img)

    if real_time_output:
        print("Images created successfully")


if __name__ == '__main__':
    mix_images(True)
