#include <windows.h>
#include <iostream>
#include "eventMonitor.h"
#include "multiScreenCap.h"
#include "cameraCap.h"
#include "config.h"

int main() {
    // 初始化所有模块
    Config::load("..\\.env");
    initializeDPI();
    setServerAddress("192.168.68.127", 80);

    // 测试环境变量是否正常
    cout << "API Key: " << Config::get("API_KEY") << endl;

    // 获取显示器数量
    int monitorCount = getMonitorCount();
    cout << "Monitor count: " << monitorCount << endl;

    // 获取当前日期和时间
    wstring date = getDateString();
    wstring time = getTimeString();
    wcout << L"Date: " << date << L", Time: " << time << endl;

    // 向树莓派发送请求
    fetchAndSaveImage("photo", "image.jpg");

    return 0;
}
