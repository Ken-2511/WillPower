#include "cameraCap.h"
#include "eventMonitor.h"
#include "multiScreenCap.h"
#include "config.h"
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>

using namespace std;

// #define DEBUG

// 截图并拉取照片
void screenCapAndFetch() {
    // 截取所有显示器
    // captureAllMonitors("test\\");
    captureAllMonitors();

    // 向树莓派发送请求
    // fetchAndSaveImage("photo", L"image.jpg");
    fetchAndSaveImage();
}

int main() {

    // 初始化所有模块
    Config::load("..\\.env");
    initializeDPI();
    setServerAddress("192.168.68.127", 80);

    // 永不退出循环，在有人操纵电脑、并且电脑连接了两个显示器的情况下，每隔30秒截图并拉取照片一次
    EventMonitor monitor;
    while (true) {
        SYSTEMTIME st;
        GetLocalTime(&st);
        #ifdef DEBUG
            cout << "Current time: " << st.wHour << ":" << st.wMinute << ":" << st.wSecond << endl;
        #endif
        if (st.wSecond % 30 == 0 && monitor.hasMoved() && getMonitorCount() == 2) {
            screenCapAndFetch();
            #ifdef DEBUG
                cout << "Screen captured and image fetched!" << endl;
            #endif
            Sleep(2000); // 休眠2秒，避免过快的截图和拉取照片
        }
        Sleep(500);
    }

    return 0;

}