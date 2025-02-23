#pragma once

#include <Windows.h>
#include <vector>
#include <string>

/// @brief 存储显示器信息
struct MonitorInfo {
    HMONITOR hMonitor;
    std::wstring deviceName;
    RECT rect;
    int index;
};

/**
 * @brief 初始化 DPI 感知，防止在高分辨率屏幕上截图异常
 */
void initializeDPI();

/**
 * @brief 返回当前系统中可用显示器的数量
 * @return 显示器数量
 */
int getMonitorCount();

/**
 * @brief 截取所有已连接的显示器，并保存到指定路径（或写死在函数内）
 */
void captureAllMonitors();
void captureAllMonitors(std::string f_name);

/**
 * @brief 以下是内部可能用到的函数
 */
std::vector<MonitorInfo> enumerateMonitors();
HBITMAP captureMonitorRect(const RECT& rect);
int saveBitmap(HBITMAP hBitmap, const std::wstring& filename);
std::wstring getDateString();
std::wstring getTimeString();
