#include <windows.h>
#include <iostream>

int main() {
    POINT cursorPos; // 用于存储鼠标位置的结构体

    std::cout << "Press Ctrl+C to exit...\n";

    while (true) {
        // 获取鼠标当前位置
        if (GetCursorPos(&cursorPos)) {
            std::cout << "Mouse Position: X=" << cursorPos.x << ", Y=" << cursorPos.y << "\r";
            std::flush(std::cout); // 刷新输出到控制台
        } else {
            std::cerr << "Failed to get cursor position. Error: " << GetLastError() << "\n";
        }

        Sleep(100); // 限制刷新频率，避免过高的 CPU 占用
    }

    return 0;
}
