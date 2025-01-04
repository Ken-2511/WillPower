#include "multiScreenCap.h"
#include <shellscalingapi.h>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <direct.h> // 用于创建目录 _wmkdir
#include <thread>
#include <chrono>

#pragma comment(lib, "gdi32.lib") // 链接 GDI 库

static std::vector<MonitorInfo> gMonitors;

// 初始化 DPI 感知
void initializeDPI() {
    HMODULE hShcore = LoadLibrary(TEXT("Shcore.dll"));
    if (hShcore) {
        typedef HRESULT(WINAPI* SetProcessDpiAwarenessFunc)(PROCESS_DPI_AWARENESS);
        SetProcessDpiAwarenessFunc setDpiAwareness =
            (SetProcessDpiAwarenessFunc)GetProcAddress(hShcore, "SetProcessDpiAwareness");
        if (setDpiAwareness) {
            setDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE);
        }
        FreeLibrary(hShcore);
    } else {
        SetProcessDPIAware();
    }
}

// 显示器枚举回调函数
BOOL CALLBACK MonitorEnumProc(HMONITOR hMonitor, HDC hdcMonitor, LPRECT lprcMonitor, LPARAM dwData) {
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
        } else {
            std::wstringstream ss;
            ss << L"MONITOR#" << m.index;
            m.deviceName = ss.str();
        }

        gMonitors.push_back(m);
    }
    return TRUE;
}

// 枚举显示器并返回信息列表
std::vector<MonitorInfo> enumerateMonitors() {
    gMonitors.clear();
    EnumDisplayMonitors(NULL, NULL, MonitorEnumProc, 0);
    return gMonitors;
}

// 截取指定矩形区域
HBITMAP captureMonitorRect(const RECT& rect) {
    int width = rect.right - rect.left;
    int height = rect.bottom - rect.top;

    if (width <= 0 || height <= 0) {
        return nullptr;
    }

    HDC hScreenDC = GetDC(NULL);
    HDC hMemoryDC = CreateCompatibleDC(hScreenDC);
    HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, width, height);

    if (hBitmap) {
        HBITMAP hOldBitmap = (HBITMAP)SelectObject(hMemoryDC, hBitmap);
        BitBlt(hMemoryDC, 0, 0, width, height, hScreenDC, rect.left, rect.top, SRCCOPY);
        SelectObject(hMemoryDC, hOldBitmap);
    }

    DeleteDC(hMemoryDC);
    ReleaseDC(NULL, hScreenDC);

    return hBitmap;
}

// 保存位图到文件
int saveBitmap(HBITMAP hBitmap, const std::wstring& filename) {
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

    DWORD dwBmpSize = ((bmp.bmWidth * biHeader.biBitCount + 31) / 32) * 4 * bmp.bmHeight;
    biHeader.biSizeImage = dwBmpSize;

    bfHeader.bfType = 0x4D42;
    bfHeader.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    bfHeader.bfSize = bfHeader.bfOffBits + biHeader.biSizeImage;

    HANDLE hDIB = GlobalAlloc(GHND, dwBmpSize);
    if (!hDIB) return 2;
    char* lpbitmap = (char*)GlobalLock(hDIB);

    HDC hdc = GetDC(NULL);
    if (!GetDIBits(hdc, hBitmap, 0, bmp.bmHeight, lpbitmap, (BITMAPINFO*)&biHeader, DIB_RGB_COLORS)) {
        GlobalUnlock(hDIB);
        GlobalFree(hDIB);
        ReleaseDC(NULL, hdc);
        return 3;
    }
    ReleaseDC(NULL, hdc);

    HANDLE hFile = CreateFileW(filename.c_str(), GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) {
        GlobalUnlock(hDIB);
        GlobalFree(hDIB);
        return 4;
    }

    DWORD written = 0;
    WriteFile(hFile, &bfHeader, sizeof(BITMAPFILEHEADER), &written, NULL);
    WriteFile(hFile, &biHeader, sizeof(BITMAPINFOHEADER), &written, NULL);
    WriteFile(hFile, lpbitmap, dwBmpSize, &written, NULL);

    CloseHandle(hFile);
    GlobalUnlock(hDIB);
    GlobalFree(hDIB);

    return 0;
}

// 获取当前日期 (yyyy-mm-dd)
std::wstring getDateString() {
    SYSTEMTIME st;
    GetLocalTime(&st);

    std::wstringstream ss;
    ss << std::setw(4) << std::setfill(L'0') << st.wYear << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wMonth << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wDay;
    return ss.str();
}

// 获取当前时间 (hh-mm-ss)
std::wstring getTimeString() {
    SYSTEMTIME st;
    GetLocalTime(&st);

    std::wstringstream ss;
    ss << std::setw(2) << std::setfill(L'0') << st.wHour << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wMinute << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wSecond;
    return ss.str();
}

// 截取所有显示器并保存
void captureAllMonitors() {
    initializeDPI();

    std::wstring dateFolder = L"D:\\screenCap\\" + getDateString();
    _wmkdir(dateFolder.c_str());

    auto monitors = enumerateMonitors();
    for (const auto& monitor : monitors) {
        std::wstring devName = monitor.deviceName;
        for (auto& ch : devName) {
            if (ch == L'\\' || ch == L'.' || ch == L':') {
                ch = L'_';
            }
        }

        std::wstringstream filePath;
        filePath << dateFolder << L"\\" << getTimeString() << L"_" << devName << L".bmp";

        HBITMAP hBitmap = captureMonitorRect(monitor.rect);
        if (hBitmap) {
            saveBitmap(hBitmap, filePath.str());
            DeleteObject(hBitmap);
        }
    }
}
