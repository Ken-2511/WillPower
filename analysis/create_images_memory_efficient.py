# Memory-efficient version of create_images.py
# This version processes images in small batches to avoid memory issues

import os
import cv2
import numpy as np
import random
from datetime import datetime, timedelta
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
PHOTOS_PATH = r"D:\cameraCap"
SCREENSHOTS_PATH = r"E:\screenCapConverted"
OUTPUT_PATH = r"C:\Users\IWMAI\Desktop"

def get_date_range():
    try:
        start_date_str = input("Enter start date (yyyy-mm-dd): ").strip()
        end_date_str = input("Enter end date (yyyy-mm-dd): ").strip()
        include_camera_str = input("Include camera photos? (y/n, default: n): ").strip().lower()
        batch_size_str = input("Batch size (default: 50): ").strip()
        num_threads_str = input("Number of threads (default: 16): ").strip()
    except EOFError:
        start_date_str = ""
        end_date_str = ""
        include_camera_str = ""
        batch_size_str = ""
        num_threads_str = ""
    
    include_camera = include_camera_str in ['y', 'yes']
    
    try:
        batch_size = int(batch_size_str) if batch_size_str else 50
        batch_size = max(10, min(batch_size, 200))  # Limit between 10 and 200
    except ValueError:
        batch_size = 50
    
    try:
        num_threads = int(num_threads_str) if num_threads_str else 16
        num_threads = max(1, min(num_threads, 32))  # Limit between 1 and 32
    except ValueError:
        num_threads = 16
    
    if not start_date_str or not end_date_str:
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
    print(f"Batch size: {batch_size}")
    print(f"Number of threads: {num_threads}")
    return start_date, end_date, include_camera, batch_size, num_threads

def get_date_list(start_date, end_date):
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    return date_list

def load_image(date: str, timestamp: str, include_camera: bool = False, target_shape=None):
    # Predefined shapes for different image types
    DISPLAY1_SHAPE = (1600, 2560)
    DISPLAY2_SHAPE = (1440, 2560)
    PHOTO_SHAPE = (2592, 1944)
    
    photo = None
    if include_camera:
        photo_path = os.path.join(PHOTOS_PATH, date, timestamp + ".jpg")
        photo = cv2.imread(photo_path) if os.path.exists(photo_path) else None
    
    # Check if DISPLAY1 file exists before reading
    display1_path = os.path.join(SCREENSHOTS_PATH, date, timestamp + "_____DISPLAY1.png")
    display1 = cv2.imread(display1_path) if os.path.exists(display1_path) else None
    
    # Try DISPLAY2 first, then DISPLAY5
    display2_path = os.path.join(SCREENSHOTS_PATH, date, timestamp + "_____DISPLAY2.png")
    display2 = None
    if os.path.exists(display2_path):
        display2 = cv2.imread(display2_path)
    else:
        display2_path = os.path.join(SCREENSHOTS_PATH, date, timestamp + "_____DISPLAY5.png")
        if os.path.exists(display2_path):
            display2 = cv2.imread(display2_path)
    
    # Check for shape consistency and warn if different
    if display1 is not None and display1.shape[:2] != DISPLAY1_SHAPE:
        print(f"Warning: DISPLAY1 shape mismatch for {date} {timestamp}. Expected {DISPLAY1_SHAPE}, got {display1.shape[:2]}")
        display1 = None
    if display2 is not None and display2.shape[:2] != DISPLAY2_SHAPE:
        print(f"Warning: DISPLAY2/5 shape mismatch for {date} {timestamp}. Expected {DISPLAY2_SHAPE}, got {display2.shape[:2]}")
        display2 = None
    if photo is not None and photo.shape[:2] != PHOTO_SHAPE:
        print(f"Warning: Camera photo shape mismatch for {date} {timestamp}. Expected {PHOTO_SHAPE}, got {photo.shape[:2]}")
        photo = None
            
    return photo, display1, display2

def get_timestamps_for_date(date: str, include_camera: bool = False):
    photos_dir = os.path.join(PHOTOS_PATH, date)
    screenshots_dir = os.path.join(SCREENSHOTS_PATH, date)
    
    if not os.path.exists(screenshots_dir):
        return []
    
    screenshots = os.listdir(screenshots_dir)
    timestamps_display1 = set()
    timestamps_display2_or_5 = set()
    
    timestamps_camera = set()
    if include_camera and os.path.exists(photos_dir):
        photos = os.listdir(photos_dir)
        for photo in photos:
            timestamp = photo.split(".")[0]
            timestamps_camera.add(timestamp)
    
    for screenshot in screenshots:
        timestamp = screenshot.split("_____")[0]
        if "DISPLAY1" in screenshot:
            timestamps_display1.add(timestamp)
        elif "DISPLAY2" in screenshot or "DISPLAY5" in screenshot:
            timestamps_display2_or_5.add(timestamp)
    
    timestamps = timestamps_display1.intersection(timestamps_display2_or_5)
    
    if include_camera and timestamps_camera:
        timestamps = timestamps.intersection(timestamps_camera)
    
    timestamps = list(timestamps)
    timestamps.sort()
    return timestamps

def get_all_timestamps(date_list, include_camera: bool = False):
    all_timestamps = []
    for date in date_list:
        timestamps = get_timestamps_for_date(date, include_camera)
        for timestamp in timestamps:
            all_timestamps.append((date, timestamp))
    
    random.shuffle(all_timestamps)
    return all_timestamps

def process_single_image(args):
    """Process a single timestamp - optimized for threading"""
    date, timestamp, include_camera = args
    try:
        images = load_image(date, timestamp, include_camera)
        
        if images[1] is not None and images[2] is not None:
            # Use actual image shapes instead of target_shape
            display1_shape = images[1].shape
            display2_shape = images[2].shape
            
            if include_camera and images[0] is not None:
                camera_image = images[0]
                photo_shape = camera_image.shape
            else:
                # Create a zero image with photo shape if no camera image
                photo_shape = (2592, 1944, 3)
                camera_image = np.zeros(photo_shape, dtype=np.uint8)
            
            # Convert to float64 immediately and return
            result = (
                camera_image.astype(np.float64),
                images[1].astype(np.float64),
                images[2].astype(np.float64),
                photo_shape,
                display1_shape,
                display2_shape,
                1  # success count
            )
            
            # Clean up
            del images, camera_image
            return result
        else:
            return None
    except Exception as e:
        print(f"Error processing {date} {timestamp}: {e}")
        return None

def process_batch_parallel(timestamp_batch, include_camera, num_threads):
    """Process a batch of timestamps in parallel"""
    # Initialize accumulators with predefined shapes
    DISPLAY1_SHAPE = (1600, 2560, 3)
    DISPLAY2_SHAPE = (1440, 2560, 3)
    PHOTO_SHAPE = (2592, 1944, 3)
    
    batch_camera = np.zeros(PHOTO_SHAPE, dtype=np.float64)
    batch_display1 = np.zeros(DISPLAY1_SHAPE, dtype=np.float64)
    batch_display2 = np.zeros(DISPLAY2_SHAPE, dtype=np.float64)
    batch_count = 0
    
    # Prepare arguments for parallel processing
    args_list = [(date, timestamp, include_camera) for date, timestamp in timestamp_batch]
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_single_image, args) for args in args_list]
        
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                camera_img, display1_img, display2_img, photo_shape, display1_shape, display2_shape, count = result
                
                # Only accumulate if shapes match expected
                if photo_shape == PHOTO_SHAPE:
                    batch_camera += camera_img
                if display1_shape == DISPLAY1_SHAPE:
                    batch_display1 += display1_img
                if display2_shape == DISPLAY2_SHAPE:
                    batch_display2 += display2_img
                
                batch_count += count
                
                # Clean up immediately
                del camera_img, display1_img, display2_img
    
    return batch_camera, batch_display1, batch_display2, batch_count

def save_images(date: str, photo: np.ndarray, display1: np.ndarray, display2: np.ndarray):
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + ".jpg"), photo)
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + "_____DISPLAY1.png"), display1)
    cv2.imwrite(os.path.join(OUTPUT_PATH, date + "_____DISPLAY5.png"), display2)

def mix_images():
    start_date, end_date, include_camera, batch_size, num_threads = get_date_range()
    date_list = get_date_list(start_date, end_date)
    all_timestamps = get_all_timestamps(date_list, include_camera)
    
    if not all_timestamps:
        print("No images found in the specified date range.")
        return
    
    print(f"Processing {len(all_timestamps)} timestamps in batches of {batch_size} using {num_threads} threads...")
    
    # Initialize accumulators with predefined shapes
    DISPLAY1_SHAPE = (1600, 2560, 3)
    DISPLAY2_SHAPE = (1440, 2560, 3)
    PHOTO_SHAPE = (2592, 1944, 3)
    
    print(f"Using predefined shapes:")
    print(f"  DISPLAY1: {DISPLAY1_SHAPE}")
    print(f"  DISPLAY2: {DISPLAY2_SHAPE}")
    print(f"  Camera: {PHOTO_SHAPE}")
    
    # Initialize accumulators
    camera_img = np.zeros(PHOTO_SHAPE, dtype=np.float64)
    display1_img = np.zeros(DISPLAY1_SHAPE, dtype=np.float64)
    display2_img = np.zeros(DISPLAY2_SHAPE, dtype=np.float64)
    valid_count = 0
    
    # Process in batches
    for i in range(0, len(all_timestamps), batch_size):
        batch = all_timestamps[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(all_timestamps) + batch_size - 1) // batch_size
        
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} images)...")
        
        batch_camera, batch_display1, batch_display2, batch_count = process_batch_parallel(
            batch, include_camera, num_threads
        )
        
        # Accumulate results
        camera_img += batch_camera
        display1_img += batch_display1
        display2_img += batch_display2
        valid_count += batch_count
        
        print(f"  Batch complete. Processed {batch_count}/{len(batch)} images successfully.")
        print(f"  Total processed: {valid_count}")
        
        # Force garbage collection
        del batch_camera, batch_display1, batch_display2
        gc.collect()
    
    if valid_count == 0:
        print("No valid images found.")
        return
    
    print("Normalizing images...")
    
    # Normalize images
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
    
    # Convert to uint8
    camera_img = camera_img.astype(np.uint8)
    display1_img = display1_img.astype(np.uint8)
    display2_img = display2_img.astype(np.uint8)
    
    # Save images
    output_date = f"{start_date}_to_{end_date}"
    save_images(output_date, camera_img, display1_img, display2_img)
    print(f"Images created successfully using {valid_count} timestamps")
    print(f"Output saved with prefix: {output_date}")

if __name__ == '__main__':
    mix_images()
