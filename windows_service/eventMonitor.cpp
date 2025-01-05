#include "eventMonitor.h"
#include <iostream>

// 静态成员初始化
EventDetector* EventDetector::instance = nullptr;

// 构造函数
EventDetector::EventDetector() 
    : running(false), eventOccurred(false) {}

// 析构函数
EventDetector::~EventDetector() {
    stop(); // 确保资源被释放
}

// 键盘钩子回调函数
LRESULT CALLBACK EventDetector::KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HC_ACTION && wParam == WM_KEYDOWN) {
        instance->eventOccurred = true;
        instance->lastEventTime = std::chrono::system_clock::now();
    }
    return CallNextHookEx(NULL, nCode, wParam, lParam);
}

// 鼠标钩子回调函数
LRESULT CALLBACK EventDetector::MouseProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode == HC_ACTION) {
        instance->eventOccurred = true;
        instance->lastEventTime = std::chrono::system_clock::now();
    }
    return CallNextHookEx(NULL, nCode, wParam, lParam);
}

// 启动监控
void EventDetector::start() {
    if (running) return;

    running = true;
    eventOccurred = false;
    lastEventTime = std::chrono::system_clock::now();
    instance = this;

    // 安装钩子
    keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, NULL, 0);
    mouseHook = SetWindowsHookEx(WH_MOUSE_LL, MouseProc, NULL, 0);

    if (!keyboardHook || !mouseHook) {
        std::cerr << "Failed to install hooks!" << std::endl;
        running = false;
        throw std::runtime_error("Failed to install hooks");
    }

    // 启动检测线程
    monitorThread = std::thread(&EventDetector::monitorLoop, this);
}

// 停止监控
void EventDetector::stop() {
    if (!running) return;

    running = false;

    // 等待线程结束
    if (monitorThread.joinable()) {
        monitorThread.join();
    }

    // 卸载钩子
    UnhookWindowsHookEx(keyboardHook);
    UnhookWindowsHookEx(mouseHook);
}

// 检测最近是否有活动
bool EventDetector::hasRecentActivity() {
    return eventOccurred;
}

// 获取上次活动时间
std::chrono::system_clock::time_point EventDetector::getLastEventTime() const {
    return lastEventTime;
}

// 检测线程循环
void EventDetector::monitorLoop() {
    while (running) {
        if (eventOccurred) {
            eventOccurred = false; // 重置事件状态
        }
        std::this_thread::sleep_for(std::chrono::seconds(1)); // 每秒检查一次
    }
}
