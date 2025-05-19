import os
import cv2
import numpy as np

# 直接复用 config.py 中定义的路径，不修改 config.py
from config import PHOTOS_PATH, SCREENSHOTS_PATH, OUTPUT_PATH

def merge_all_images(real_time_output=False):
    """
    遍历所有日期文件夹，将所有日期的相机图片、DISPLAY1、DISPLAY2截图分别累加，
    并输出三张融合后的图像。归一化处理逻辑与 create_images.py 中的 mix_images 保持一致。
    """

    if real_time_output:
        print("[merge_all_images] 开始处理所有日期文件夹……")

    # 1) 获取同时存在于相机目录和截图目录中的日期文件夹
    all_dates = get_all_common_dates(PHOTOS_PATH, SCREENSHOTS_PATH)
    if real_time_output:
        print("[merge_all_images] 发现以下日期需要处理：", all_dates)

    # 初始化累加器
    camera_accum = None
    display1_accum = None
    display2_accum = None

    # 用于记录是否成功累加过任何图像
    has_accumulated = False

    # 2) 遍历每个日期，将当日所有同时存在的相机图和截图累加到全局
    for date_str in all_dates:
        timestamps = get_timestamps_for_date(date_str)
        if real_time_output:
            print(f"[merge_all_images] 日期 {date_str}，可用时间戳数：{len(timestamps)}")

        for ts in timestamps:
            # 分别读取相机图、DISPLAY1、DISPLAY2
            if real_time_output:
                print(f"[merge_all_images] 处理时间戳：{ts}\r", end="")
            photo_path = os.path.join(PHOTOS_PATH, date_str, ts + ".jpg")
            d1_path    = os.path.join(SCREENSHOTS_PATH, date_str, ts + "_____DISPLAY1.bmp")
            d2_path    = os.path.join(SCREENSHOTS_PATH, date_str, ts + "_____DISPLAY2.bmp")

            photo    = cv2.imread(photo_path)
            display1 = cv2.imread(d1_path)
            display2 = cv2.imread(d2_path)

            # 如果有任意一张图片读取失败，则跳过
            if photo is None or display1 is None or display2 is None:
                if real_time_output:
                    print(f"[merge_all_images] 跳过无法读取的文件: {ts}")
                continue

            # 首次累加时初始化容器
            if camera_accum is None:
                camera_accum  = np.zeros_like(photo,    dtype=np.float64)
                display1_accum = np.zeros_like(display1, dtype=np.float64)
                display2_accum = np.zeros_like(display2, dtype=np.float64)

            # 将所有图像累加
            camera_accum  += photo.astype(np.float64)
            display1_accum += display1.astype(np.float64)
            display2_accum += display2.astype(np.float64)

            has_accumulated = True
        print()

    if not has_accumulated:
        if real_time_output:
            print("[merge_all_images] 未找到任何可用图像，结束。")
        return

    # 3) 对累加结果进行“原逻辑”归一化：减去最小值，除以最大值，再乘以255
    if real_time_output:
        print("[merge_all_images] 开始归一化处理（与 mix_images 同样的线性拉伸逻辑）……")

    camera_final  = normalize_0_255(camera_accum)
    display1_final = normalize_0_255(display1_accum)
    display2_final = normalize_0_255(display2_accum)

    # 4) 保存最终结果到 OUTPUT_PATH 下
    camera_out  = os.path.join(OUTPUT_PATH, "all_dates.jpg")
    display1_out = os.path.join(OUTPUT_PATH, "all_dates_____DISPLAY1.bmp")
    display2_out = os.path.join(OUTPUT_PATH, "all_dates_____DISPLAY2.bmp")

    cv2.imwrite(camera_out,  camera_final)
    cv2.imwrite(display1_out, display1_final)
    cv2.imwrite(display2_out, display2_final)

    if real_time_output:
        print("[merge_all_images] 所有日期图像融合完成！输出文件：")
        print("  -", camera_out)
        print("  -", display1_out)
        print("  -", display2_out)


def get_all_common_dates(photos_path: str, screenshots_path: str):
    """
    获取同时存在于相机目录和截图目录中的公共日期文件夹列表。
    """
    if not os.path.exists(photos_path) or not os.path.exists(screenshots_path):
        return []

    # 列举相机路径与截图路径下的所有子文件夹
    photo_dates = [d for d in os.listdir(photos_path)
                   if os.path.isdir(os.path.join(photos_path, d))]
    screen_dates = [d for d in os.listdir(screenshots_path)
                    if os.path.isdir(os.path.join(screenshots_path, d))]

    # 取交集
    common = sorted(list(set(photo_dates).intersection(set(screen_dates))))
    return common


def get_timestamps_for_date(date_str: str):
    """
    根据原 create_images.py 的逻辑，获取给定日期下拥有：
      - 相机照片 (xxxx.jpg)
      - DISPLAY1 (xxxx_____DISPLAY1.bmp)
      - DISPLAY2 (xxxx_____DISPLAY2.bmp)
    的完整时间戳列表。
    """
    # 相机目录
    photo_dir = os.path.join(PHOTOS_PATH, date_str)
    # 截图目录
    screen_dir = os.path.join(SCREENSHOTS_PATH, date_str)

    if not os.path.exists(photo_dir) or not os.path.exists(screen_dir):
        return []

    # 列出文件名
    photos = os.listdir(photo_dir)
    screens = os.listdir(screen_dir)

    # 分别记录下 camera、display1、display2 的时间戳
    timestamps_camera = set()
    timestamps_display1 = set()
    timestamps_display2 = set()

    for ph in photos:
        # 相机照片形如 "hh-mm-ss.jpg"
        stamp = os.path.splitext(ph)[0]  # 去掉 .jpg
        timestamps_camera.add(stamp)

    for sc in screens:
        # 截图文件形如 "hh-mm-ss_____DISPLAY1.bmp" / "hh-mm-ss_____DISPLAY2.bmp"
        stamp = sc.split("_____")[0]
        if "DISPLAY1" in sc:
            timestamps_display1.add(stamp)
        elif "DISPLAY2" in sc:
            timestamps_display2.add(stamp)

    # 三者交集才算有效
    valid_timestamps = timestamps_camera.intersection(
        timestamps_display1, timestamps_display2
    )
    return sorted(valid_timestamps)


def normalize_0_255(img_accum: np.ndarray):
    """
    采用 create_images.py 同样的逻辑进行线性归一化：
      1) 减去 min
      2) 除以 max
      3) 乘以 255
    """
    min_val = img_accum.min()
    max_val = img_accum.max()
    # 若整幅图都是同一个值，避免除 0
    if max_val == min_val:
        return np.zeros_like(img_accum, dtype=np.uint8)

    # 原逻辑：img -= min; img /= max; img *= 255
    img_accum = img_accum - min_val
    img_accum = img_accum / (max_val - min_val)
    img_accum = img_accum * 255.0
    return img_accum.astype(np.uint8)


if __name__ == "__main__":
    merge_all_images(real_time_output=True)