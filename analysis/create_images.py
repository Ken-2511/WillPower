# this file is for creating the images from a specific date range
# three images to be created:
# 1. the photo taken by the raspberry pi camera, filename: "hh-mm-ss.jpg"
# 2. the screenshot on the laptop screen, filename: "hh-mm-ss_____DISPLAY1.bmp"
# 3. the screenshot on the main screen, filename: "hh-mm-ss_____DISPLAY2.bmp"

import os
import cv2
import numpy as np
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
PHOTOS_PATH = r"D:\cameraCap"
SCREENSHOTS_PATH = r"D:\screenCap"
OUTPUT_PATH = r"C:\Users\IWMAI\Desktop"

# Get date range from user
def get_date_range():
    try:
        start_date_str = input("Enter start date (yyyy-mm-dd): ").strip()
        end_date_str = input("Enter end date (yyyy-mm-dd): ").strip()
        include_camera_str = input("Include camera photos? (y/n, default: n): ").strip().lower()
        threads_str = input("Number of threads (default: 4): ").strip()
    except EOFError:
        # Handle case when running in non-interactive mode
        start_date_str = ""
        end_date_str = ""
        include_camera_str = ""
        threads_str = ""
    
    # Parse include camera option
    include_camera = include_camera_str in ['y', 'yes']
    
    # Parse number of threads
    try:
        num_threads = int(threads_str) if threads_str else 4
        num_threads = max(1, min(num_threads, 16))  # Limit between 1 and 16
    except ValueError:
        num_threads = 4
    
    # Add batch size for memory management
    batch_size = 50  # Process images in batches to avoid memory issues
    
    if not start_date_str or not end_date_str:
        # Default range: from 2025-01-01 to today
        start_date = datetime(2025, 1, 1).date()
        end_date = datetime.now().date()
        print(f"Using default date range: {start_date} to {end_date}")
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Using default range.")
            start_date = datetime(2025, 1, 1).date()
            end_date = datetime.now().date()
    
    print(f"Include camera photos: {include_camera}")
    print(f"Number of threads: {num_threads}")
    print(f"Batch size: {batch_size}")
    return start_date, end_date, include_camera, num_threads, batch_size

# Generate list of date strings in the range
def get_date_list(start_date, end_date):
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    return date_list


# load three images from the timestamp as numpy array
def load_image(date: str, timestamp: str, include_camera: bool = False, target_shape=None):
    # load the photo taken by the raspberry pi camera
    photo = None
    if include_camera:
        photo_path = os.path.join(PHOTOS_PATH, date, timestamp + ".jpg")
        photo = cv2.imread(photo_path) if os.path.exists(photo_path) else None
    
    # load the screenshot on the laptop screen
    display1 = cv2.imread(os.path.join(SCREENSHOTS_PATH, date, timestamp + "_____DISPLAY1.png"))
    # load the screenshot on the main screen  
    display2 = cv2.imread(os.path.join(SCREENSHOTS_PATH, date, timestamp + "_____DISPLAY5.png"))
    
    # Resize images to target shape if provided
    if target_shape is not None:
        if display1 is not None:
            display1 = cv2.resize(display1, (target_shape[1], target_shape[0]))
        if display2 is not None:
            display2 = cv2.resize(display2, (target_shape[1], target_shape[0]))
        if photo is not None:
            photo = cv2.resize(photo, (target_shape[1], target_shape[0]))
    
    return photo, display1, display2


def save_images(date: str, photo: np.ndarray, display1: np.ndarray, display2: np.ndarray):
    # save the photo taken by the raspberry pi camera
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + ".jpg"), photo)
    # save the screenshot on the laptop screen
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + "_____DISPLAY1.png"), display1)
    # save the screenshot on the main screen
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + "_____DISPLAY5.png"), display2)


# get the timestamps that we have all the three images for a specific date
def get_timestamps_for_date(date: str, include_camera: bool = False):
    photos_dir = os.path.join(PHOTOS_PATH, date)
    screenshots_dir = os.path.join(SCREENSHOTS_PATH, date)
    
    # Check if screenshots directory exists (photos directory is optional)
    if not os.path.exists(screenshots_dir):
        return []
    
    # list all the files in the screenshots path
    screenshots = os.listdir(screenshots_dir)
    # get the timestamps that we have both display images
    timestamps_display1 = set()
    timestamps_display5 = set()
    
    # If photos directory exists and user wants camera photos, get camera timestamps
    timestamps_camera = set()
    if include_camera and os.path.exists(photos_dir):
        photos = os.listdir(photos_dir)
        for photo in photos:
            # get the timestamp from the photo
            timestamp = photo.split(".")[0]
            timestamps_camera.add(timestamp)
    
    for screenshot in screenshots:
        # get the timestamp from the screenshot
        timestamp = screenshot.split("_____")[0]
        if "DISPLAY1" in screenshot:
            timestamps_display1.add(timestamp)
        elif "DISPLAY5" in screenshot:
            timestamps_display5.add(timestamp)
    
    # get the timestamps that we have both display images
    timestamps = timestamps_display1.intersection(timestamps_display5)
    
    # If camera photos are requested and exist, only include timestamps that have camera photos too
    if include_camera and timestamps_camera:
        timestamps = timestamps.intersection(timestamps_camera)
    
    # convert to list and sort
    timestamps = list(timestamps)
    timestamps.sort()
    return timestamps


# get all timestamps from all dates in the range
def get_all_timestamps(date_list, include_camera: bool = False):
    all_timestamps = []
    for date in date_list:
        timestamps = get_timestamps_for_date(date, include_camera)
        for timestamp in timestamps:
            all_timestamps.append((date, timestamp))
    
    # Shuffle the timestamps to detect problems earlier
    random.shuffle(all_timestamps)
    return all_timestamps


# Thread-safe function to process a single timestamp
def process_single_timestamp(args):
    date, timestamp, include_camera, target_shape, thread_id = args
    try:
        images = load_image(date, timestamp, include_camera, target_shape)
        
        # Check if display images loaded successfully
        if images[1] is not None and images[2] is not None:
            # Use black placeholder if camera image is missing or not requested
            camera_image = images[0] if images[0] is not None else np.zeros((target_shape[0], target_shape[1], 3), dtype=np.uint8)
            
            return {
                'success': True,
                'camera': camera_image.astype(np.float64),
                'display1': images[1].astype(np.float64),
                'display2': images[2].astype(np.float64),
                'timestamp': f"{date} {timestamp}"
            }
        else:
            return {
                'success': False,
                'timestamp': f"{date} {timestamp}",
                'error': 'missing display files'
            }
    except Exception as e:
        return {
            'success': False,
            'timestamp': f"{date} {timestamp}",
            'error': str(e)
        }


def mix_images(real_time_output=False, num_threads=4):
    # Get date range from user
    start_date, end_date, include_camera, num_threads = get_date_range()
    date_list = get_date_list(start_date, end_date)
    
    # Get all timestamps from the date range
    all_timestamps = get_all_timestamps(date_list, include_camera)
    
    if not all_timestamps:
        print("No images found in the specified date range.")
        return
    
    # create the images
    if real_time_output:
        print(f"Creating images from {len(all_timestamps)} timestamps...")
    
    # Load first image to get dimensions and determine target shape
    first_date, first_timestamp = all_timestamps[0]
    images = load_image(first_date, first_timestamp, include_camera)
    
    # Check if at least display images are available
    if images[1] is None or images[2] is None:
        print("Error loading display images. Please check paths and file existence.")
        return
    
    # Use display1 dimensions as target shape for consistency
    target_shape = images[1].shape[:2]  # (height, width)
    if real_time_output:
        print(f"Target image shape: {target_shape}")
    
    # Reload first image with target shape
    images = load_image(first_date, first_timestamp, include_camera, target_shape)
    
    # Create placeholder for camera image if it doesn't exist or not requested
    if images[0] is None:
        if include_camera:
            print("Camera images not found. Using black placeholder for camera images.")
        else:
            print("Camera images not requested. Using black placeholder.")
        # Create a black image with target dimensions
        placeholder_camera = np.zeros((target_shape[0], target_shape[1], 3), dtype=np.uint8)
        images = (placeholder_camera, images[1], images[2])
    
    camera_img = np.zeros_like(images[0], dtype=np.float64)
    display1_img = np.zeros_like(images[1], dtype=np.float64)
    display2_img = np.zeros_like(images[2], dtype=np.float64)
    
    # Prepare arguments for threading
    thread_args = [(date, timestamp, include_camera, target_shape, i) 
                   for i, (date, timestamp) in enumerate(all_timestamps)]
    
    # Process images using thread pool
    valid_count = 0
    processed_count = 0
    lock = threading.Lock()
    
    if real_time_output:
        print(f"Processing with {num_threads} threads...")
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit all tasks
        future_to_args = {executor.submit(process_single_timestamp, args): args 
                         for args in thread_args}
        
        # Process completed tasks
        for future in as_completed(future_to_args):
            result = future.result()
            processed_count += 1
            
            if result['success']:
                # Thread-safe accumulation
                with lock:
                    camera_img += result['camera']
                    display1_img += result['display1']
                    display2_img += result['display2']
                    valid_count += 1
                
                if real_time_output:
                    print(f"[{processed_count}/{len(all_timestamps)}] ✓ {result['timestamp']}")
            else:
                if real_time_output:
                    print(f"[{processed_count}/{len(all_timestamps)}] ✗ {result['timestamp']} ({result['error']})")
    
    if valid_count == 0:
        print("No valid images found.")
        return
    
    # restrict the value from 0 to 255
    if real_time_output:
        print("Normalizing the images...")
    
    # Handle camera image normalization (might be all zeros if no camera photos)
    if camera_img.max() > 0:
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
    output_date = f"{start_date}_to_{end_date}"
    save_images(output_date, camera_img, display1_img, display2_img)
    if real_time_output:
        print(f"Images created successfully using {valid_count} timestamps")
        print(f"Output saved with prefix: {output_date}")


if __name__ == '__main__':
    mix_images(True)
