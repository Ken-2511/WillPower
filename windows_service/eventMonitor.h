#ifndef EVENT_DETECTOR_H
#define EVENT_DETECTOR_H

#include <windows.h>
#include <thread>
#include <atomic>
#include <chrono>

class EventDetector {
public:
    EventDetector();
    ~EventDetector();

    void start();                 // 启动监控
    void stop();                  // 停止监控
    bool hasRecentActivity();     // 检测最近是否有活动
    std::chrono::system_clock::time_point getLastEventTime() const; // 获取上次活动时间

private:
    static LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam);
    static LRESULT CALLBACK MouseProc(int nCode, WPARAM wParam, LPARAM lParam);

    void monitorLoop();           // 独立线程循环检测

    std::atomic<bool> running;    // 控制线程运行
    std::atomic<bool> eventOccurred; // 记录是否有事件发生
    std::thread monitorThread;    // 检测线程

    std::chrono::system_clock::time_point lastEventTime; // 上次活动时间

    HHOOK keyboardHook;           // 键盘钩子句柄
    HHOOK mouseHook;              // 鼠标钩子句柄

    static EventDetector* instance; // 用于回调函数访问类成员
};

#endif // EVENT_DETECTOR_H
