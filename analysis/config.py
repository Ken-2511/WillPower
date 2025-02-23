# this file contains the configuration for the analysis
from datetime import datetime

# Path to the images
PHOTOS_PATH = r"D:\cameraCap"
SCREENSHOTS_PATH = r"D:\screenCap"

# default date of the images
DATE = input("Enter the date of the images (yyyy-mm-dd): ")
if DATE == "":
    DATE = str(datetime.now().date())

# file output path
OUTPUT_PATH = r"C:\Users\IWMAI\Desktop"

if __name__ == '__main__':
    print(PHOTOS_PATH)
    print(SCREENSHOTS_PATH)
    print(DATE)