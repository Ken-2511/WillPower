/*
取消使用windows api，因为总是调不好。
在有限的时间里，用最简单的逻辑达到近似的效果吧！

之前的计划：使用钩子监控鼠标和键盘事件，如果检测到有事件就说明电脑前有人
现在的计划：只获取鼠标位置，如果鼠标位置变化就说明电脑前有人
*/

#include "eventMonitor.h"
#include <iostream>
#include <windows.h>

#define DEFAULT_INTERVAL 5 * 60 * 1000 // 默认时间间隔为5分钟

using namespace std;

EventMonitor::EventMonitor() {
    lastMoveTime = GetTickCount64();
    if (!GetCursorPos(&lastCursorPos)) {
        // 输出错误信息但不退出程序
        cerr << "Failed to get cursor position. Error: " << GetLastError() << "\n";
        lastCursorPos.x = 0;
        lastCursorPos.y = 0;
    }
}

EventMonitor::~EventMonitor() {
}

POINT EventMonitor::getLastCursorPos() const {
    return lastCursorPos;
}

DWORD EventMonitor::getLastMoveTime() const {
    return lastMoveTime;
}

void EventMonitor::update() {
    POINT cursorPos;
    if (!GetCursorPos(&cursorPos)) {
        // 输出错误信息但不退出程序
        cerr << "Failed to get cursor position. Error: " << GetLastError() << "\n";
        return;
    }

    if (cursorPos.x != lastCursorPos.x || cursorPos.y != lastCursorPos.y) {
        lastMoveTime = GetTickCount64();
        lastCursorPos = cursorPos;
    }
}

bool EventMonitor::hasMoved(int interval) const {
    return GetTickCount64() - lastMoveTime < interval;
}

bool EventMonitor::hasMoved() const {
    return hasMoved(DEFAULT_INTERVAL);
}