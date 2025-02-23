/*
取消使用windows api，因为总是调不好。
在有限的时间里，用最简单的逻辑达到近似的效果吧！

之前的计划：使用钩子监控鼠标和键盘事件，如果检测到有事件就说明电脑前有人
现在的计划：只获取鼠标位置，如果鼠标位置变化就说明电脑前有人
*/

#pragma once

#include <iostream>
#include <windows.h>

using namespace std;

class EventMonitor {
public:
    // constructor
    EventMonitor();

    // destructor
    ~EventMonitor();

    // 检测鼠标在规定时间内有没有移动
    bool hasMoved(int interval) const;
    bool hasMoved() const; // 默认时间间隔为5分钟

    // 获取鼠标当前位置
    POINT getLastCursorPos() const;

    // 获取鼠标上一次移动时间
    DWORD getLastMoveTime() const;

    // 更新函数，获取静默地获取鼠标位置信息，判断鼠标是否移动
    void update();

private:
    // 鼠标上一次移动时间
    DWORD lastMoveTime;

    // 鼠标上一次位置
    POINT lastCursorPos;
};
