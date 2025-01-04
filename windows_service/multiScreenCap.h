#pragma once

#include <Windows.h>
#include <vector>
#include <string>


struct MonitorInfo {
    HMONITOR hMonitor;
    std::wstring deviceName;
    RECT rect;
    int index;
};

void initializeDPI();

std::vector<MonitorInfo> enumerateMonitors();

HBITMAP captureMonitorRect(const RECT& rect);

int saveBitmap(HBITMAP hBitmap, const std::wstring& filename);

std::wstring getDateString();

std::wstring getTimeString();

void captureAllMonitors();
