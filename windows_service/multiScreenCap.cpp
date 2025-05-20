#include "multiScreenCap.h"

#include <direct.h>  // 用于创建目录 _wmkdir
#include <shellscalingapi.h>

#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>

#include "utils.h"

using std::string;

#pragma comment(lib, "gdi32.lib")  // 链接 GDI 库

// 存储全局的显示器信息
static std::vector<MonitorInfo> gMonitors;

//-----------------------------------------
// 1. DPI 初始化
//-----------------------------------------
void initializeDPI() {
    HMODULE hShcore = LoadLibrary(TEXT("Shcore.dll"));
    if (hShcore) {
        typedef HRESULT(WINAPI * SetProcessDpiAwarenessFunc)(PROCESS_DPI_AWARENESS);
        SetProcessDpiAwarenessFunc setDpiAwareness =
            (SetProcessDpiAwarenessFunc)GetProcAddress(hShcore,
                                                       "SetProcessDpiAwareness");
        if (setDpiAwareness) {
            setDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE);
        }
        FreeLibrary(hShcore);
    } else {
        // 如果无法使用 Shcore.dll，就退回到传统的 SetProcessDPIAware
        SetProcessDPIAware();
    }
}

//-----------------------------------------
// 2. 显示器枚举回调函数
//-----------------------------------------
BOOL CALLBACK MonitorEnumProc(HMONITOR hMonitor, HDC hdcMonitor,
                              LPRECT lprcMonitor, LPARAM dwData) {
    static int monitorIndex = 0;

    MONITORINFOEXW monInfo;
    monInfo.cbSize = sizeof(MONITORINFOEXW);
    if (GetMonitorInfoW(hMonitor, &monInfo)) {
        MonitorInfo m;
        m.hMonitor = hMonitor;
        m.rect = monInfo.rcMonitor;
        m.index = monitorIndex++;

        // 获取设备名称
        std::wstring devName(monInfo.szDevice);
        if (!devName.empty()) {
            m.deviceName = devName;
            for (auto &ch : m.deviceName) {
                if (ch == L'\\' || ch == L'.' || ch == L':') {
                    ch = L'_';
                }
            }
        } else {
            std::wstringstream ss;
            ss << L"MONITOR#" << m.index;
            m.deviceName = ss.str();
        }
        gMonitors.push_back(m);
    }
    return TRUE;
}

//-----------------------------------------
// 3. 枚举显示器，填充全局 gMonitors
//-----------------------------------------
std::vector<MonitorInfo> enumerateMonitors() {
    gMonitors.clear();
    EnumDisplayMonitors(nullptr, nullptr, MonitorEnumProc, 0);
    return gMonitors;
}

//-----------------------------------------
// 4. 获取当前系统中的显示器数量
//-----------------------------------------
int getMonitorCount() {
    // 每次调用都重新枚举，确保热插拔显示器时也能更新
    auto monitors = enumerateMonitors();
    return static_cast<int>(monitors.size());
}

//-----------------------------------------
// 5. 截取指定矩形区域
//-----------------------------------------
HBITMAP captureMonitorRect(const RECT &rect) {
    int width = rect.right - rect.left;
    int height = rect.bottom - rect.top;
    if (width <= 0 || height <= 0) {
        return nullptr;
    }

    HDC hScreenDC = GetDC(nullptr);
    HDC hMemoryDC = CreateCompatibleDC(hScreenDC);
    HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, width, height);

    if (hBitmap) {
        HBITMAP hOldBitmap = (HBITMAP)SelectObject(hMemoryDC, hBitmap);
        BitBlt(hMemoryDC, 0, 0, width, height, hScreenDC, rect.left, rect.top,
               SRCCOPY);
        SelectObject(hMemoryDC, hOldBitmap);
    }

    DeleteDC(hMemoryDC);
    ReleaseDC(nullptr, hScreenDC);

    return hBitmap;
}

//-----------------------------------------
// 6. 保存位图到文件
//-----------------------------------------
int saveBitmap(HBITMAP hBitmap, const std::wstring &filename) {
    if (!hBitmap) return 1;

    BITMAP bmp;
    GetObject(hBitmap, sizeof(BITMAP), &bmp);

    BITMAPFILEHEADER bfHeader = {0};
    BITMAPINFOHEADER biHeader = {0};

    biHeader.biSize = sizeof(BITMAPINFOHEADER);
    biHeader.biWidth = bmp.bmWidth;
    biHeader.biHeight = bmp.bmHeight;
    biHeader.biPlanes = 1;
    biHeader.biBitCount = bmp.bmBitsPixel;
    biHeader.biCompression = BI_RGB;

    DWORD dwBmpSize =
        ((bmp.bmWidth * biHeader.biBitCount + 31) / 32) * 4 * bmp.bmHeight;
    biHeader.biSizeImage = dwBmpSize;

    bfHeader.bfType = 0x4D42;  // "BM"
    bfHeader.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    bfHeader.bfSize = bfHeader.bfOffBits + biHeader.biSizeImage;

    HANDLE hDIB = GlobalAlloc(GHND, dwBmpSize);
    if (!hDIB) return 2;

    char *lpbitmap = (char *)GlobalLock(hDIB);

    HDC hdc = GetDC(nullptr);
    if (!GetDIBits(hdc, hBitmap, 0, bmp.bmHeight, lpbitmap,
                   (BITMAPINFO *)&biHeader, DIB_RGB_COLORS)) {
        GlobalUnlock(hDIB);
        GlobalFree(hDIB);
        ReleaseDC(nullptr, hdc);
        return 3;
    }
    ReleaseDC(nullptr, hdc);

    HANDLE hFile = CreateFileW(filename.c_str(), GENERIC_WRITE, 0, nullptr,
                               CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (hFile == INVALID_HANDLE_VALUE) {
        GlobalUnlock(hDIB);
        GlobalFree(hDIB);
        return 4;
    }

    DWORD written = 0;
    WriteFile(hFile, &bfHeader, sizeof(BITMAPFILEHEADER), &written, nullptr);
    WriteFile(hFile, &biHeader, sizeof(BITMAPINFOHEADER), &written, nullptr);
    WriteFile(hFile, lpbitmap, dwBmpSize, &written, nullptr);

    CloseHandle(hFile);
    GlobalUnlock(hDIB);
    GlobalFree(hDIB);

    return 0;
}

//-----------------------------------------
// 7. 获取当前日期 (yyyy-mm-dd)
//-----------------------------------------
// 放到了utils.cpp中

//-----------------------------------------
// 8. 获取当前时间 (hh-mm-ss)
//-----------------------------------------
// 放到了utils.cpp中

//-----------------------------------------
// 9. 截取显示器
//-----------------------------------------
void captureMonitor(const std::wstring &filename, const MonitorInfo &monitor) {
    // 初始化 DPI（可选，看你需求）
    initializeDPI();

    // 截图并保存
    HBITMAP hBitmap = captureMonitorRect(monitor.rect);
    if (hBitmap) {
        std::wstring tempFileName = monitor.deviceName + L".bmp";
        saveBitmap(hBitmap, tempFileName);
        std::wcout << tempFileName << std::endl;
        DeleteObject(hBitmap);
        // 转成png
        std::string tempFileNameA(tempFileName.begin(), tempFileName.end());
        std::string filenameA(filename.begin(), filename.end());
        bmp2png(tempFileNameA.c_str(), filenameA.c_str());
        std::wcout << filename << std::endl;
        // 删除临时文件
        DeleteFileW(tempFileName.c_str());
    }
}

void captureAllMonitors(const std::wstring &folderName,
                        const std::wstring &time) {
    // 获取所有显示器信息
    std::vector<MonitorInfo> monitors = enumerateMonitors();

    for (const auto &monitor : monitors) {
        // 截取每个显示器
        std::wstringstream filePathScreen;
        filePathScreen << folderName << L"\\" << time << L"_" << monitor.deviceName
                       << L".png";
        captureMonitor(filePathScreen.str(), monitor);
    }
}