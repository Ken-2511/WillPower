#include "multiScreenCap.h"
#include <shellscalingapi.h>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <direct.h> // 用于创建目录 _wmkdir
#include <thread>
#include <chrono>

#pragma comment(lib, "gdi32.lib") // 链接 GDI 库

// 存储全局的显示器信息
static std::vector<MonitorInfo> gMonitors;

//-----------------------------------------
// 1. DPI 初始化
//-----------------------------------------
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
        // 如果无法使用 Shcore.dll，就退回到传统的 SetProcessDPIAware
        SetProcessDPIAware();
    }
}

//-----------------------------------------
// 2. 显示器枚举回调函数
//-----------------------------------------
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
HBITMAP captureMonitorRect(const RECT& rect) {
    int width  = rect.right - rect.left;
    int height = rect.bottom - rect.top;
    if (width <= 0 || height <= 0) {
        return nullptr;
    }

    HDC hScreenDC = GetDC(nullptr);
    HDC hMemoryDC = CreateCompatibleDC(hScreenDC);
    HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, width, height);

    if (hBitmap) {
        HBITMAP hOldBitmap = (HBITMAP)SelectObject(hMemoryDC, hBitmap);
        BitBlt(hMemoryDC, 0, 0, width, height, hScreenDC, rect.left, rect.top, SRCCOPY);
        SelectObject(hMemoryDC, hOldBitmap);
    }

    DeleteDC(hMemoryDC);
    ReleaseDC(nullptr, hScreenDC);

    return hBitmap;
}

//-----------------------------------------
// 6. 保存位图到文件
//-----------------------------------------
int saveBitmap(HBITMAP hBitmap, const std::wstring& filename) {
    if (!hBitmap) return 1;

    BITMAP bmp;
    GetObject(hBitmap, sizeof(BITMAP), &bmp);

    BITMAPFILEHEADER bfHeader = { 0 };
    BITMAPINFOHEADER biHeader = { 0 };

    biHeader.biSize       = sizeof(BITMAPINFOHEADER);
    biHeader.biWidth      = bmp.bmWidth;
    biHeader.biHeight     = bmp.bmHeight;
    biHeader.biPlanes     = 1;
    biHeader.biBitCount   = bmp.bmBitsPixel;
    biHeader.biCompression = BI_RGB;

    DWORD dwBmpSize = ((bmp.bmWidth * biHeader.biBitCount + 31) / 32) * 4 * bmp.bmHeight;
    biHeader.biSizeImage = dwBmpSize;

    bfHeader.bfType    = 0x4D42; // "BM"
    bfHeader.bfOffBits = sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    bfHeader.bfSize    = bfHeader.bfOffBits + biHeader.biSizeImage;

    HANDLE hDIB = GlobalAlloc(GHND, dwBmpSize);
    if (!hDIB) return 2;

    char* lpbitmap = (char*)GlobalLock(hDIB);

    HDC hdc = GetDC(nullptr);
    if (!GetDIBits(hdc, hBitmap, 0, bmp.bmHeight, lpbitmap, (BITMAPINFO*)&biHeader, DIB_RGB_COLORS)) {
        GlobalUnlock(hDIB);
        GlobalFree(hDIB);
        ReleaseDC(nullptr, hdc);
        return 3;
    }
    ReleaseDC(nullptr, hdc);

    HANDLE hFile = CreateFileW(
        filename.c_str(),
        GENERIC_WRITE, 0, nullptr,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );
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
std::wstring getDateString() {
    SYSTEMTIME st;
    GetLocalTime(&st);

    std::wstringstream ss;
    ss << std::setw(4) << std::setfill(L'0') << st.wYear << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wMonth << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wDay;
    return ss.str();
}

//-----------------------------------------
// 8. 获取当前时间 (hh-mm-ss)
//-----------------------------------------
std::wstring getTimeString() {
    SYSTEMTIME st;
    GetLocalTime(&st);

    std::wstringstream ss;
    ss << std::setw(2) << std::setfill(L'0') << st.wHour << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wMinute << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wSecond;
    return ss.str();
}

//-----------------------------------------
// 9. 截取所有显示器
//-----------------------------------------
void captureAllMonitors() {
    // 初始化 DPI（可选，看你需求）
    initializeDPI();

    // 枚举所有显示器
    auto monitors = enumerateMonitors();

    // 生成当日文件夹路径
    std::wstring dateFolder = L"D:\\screenCap\\" + getDateString();
    _wmkdir(dateFolder.c_str()); // 如果文件夹已存在，不会报错

    for (const auto& monitor : monitors) {
        // 处理设备名中的特殊字符，防止生成非法文件名
        std::wstring devName = monitor.deviceName;
        for (auto& ch : devName) {
            if (ch == L'\\' || ch == L'.' || ch == L':') {
                ch = L'_';
            }
        }

        // 拼接完整的文件路径
        std::wstringstream filePath;
        filePath << dateFolder << L"\\" << getTimeString() << L"_" << devName << L".bmp";

        // 截图并保存
        HBITMAP hBitmap = captureMonitorRect(monitor.rect);
        if (hBitmap) {
            saveBitmap(hBitmap, filePath.str());
            DeleteObject(hBitmap);
        }
    }
}
