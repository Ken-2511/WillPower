#include <iostream>
#include <iomanip>
#include <thread>
#include <atomic>
#include <chrono>
#include <windows.h>
#include "eventMonitor.h"

// 打印带时间戳的日志
void printWithTimestamp(const std::string& message) {
    auto now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
    std::cout << "[" << std::put_time(std::localtime(&now), "%Y-%m-%d %H:%M:%S") << "] " << message << std::endl;
}

// 定时任务线程：每隔 5 秒检查事件状态
void periodicCheck(EventDetector& detector, std::atomic<bool>& running) {
    while (running) {
        if (detector.hasRecentActivity()) {
            printWithTimestamp("Activity detected!");
        } else {
            printWithTimestamp("No activity detected.");
        }
        std::this_thread::sleep_for(std::chrono::seconds(1)); // 每 5 秒检查一次
    }
}

int main() {
    try {
        EventDetector detector;

        // 启动事件监控
        detector.start();
        printWithTimestamp("Event monitoring started. Press Ctrl+C to exit.");

        // 控制线程运行状态
        std::atomic<bool> running(true);

        // 启动定时任务线程
        std::thread checkerThread(periodicCheck, std::ref(detector), std::ref(running));

        // 消息循环（主线程）
        MSG msg;
        while (true) {
            // if (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) { // 非阻塞式消息处理
            //     if (msg.message == WM_QUIT) break;         // 接收 WM_QUIT 消息退出
            //     TranslateMessage(&msg);
            //     DispatchMessage(&msg);
            // }

            // // 主线程不阻塞，快速处理其他任务
            // std::this_thread::sleep_for(std::chrono::milliseconds(10));
            DWORD result = MsgWaitForMultipleObjects(0, NULL, FALSE, 10, QS_ALLINPUT);
            if (result == WAIT_OBJECT_0) {
                // 事件被触发
                std::cout << "Event triggered!" << std::endl;
            } else if (result == WAIT_OBJECT_0 + 1) {
                // 有待处理的消息
                MSG msg;
                while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE)) {
                    TranslateMessage(&msg);
                    DispatchMessage(&msg);
                }
            } else {
                // 其他情况
                std::cerr << "Wait failed or timed out: " << GetLastError() << std::endl;
            }
        }

        // 停止线程
        running = false;
        checkerThread.join();

        // 停止事件监控
        detector.stop();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return -1;
    }

    return 0;
}
