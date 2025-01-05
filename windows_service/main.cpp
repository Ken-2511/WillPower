#include "cameraCap.h"
#include "eventMonitor.h"
#include "multiScreenCap.h"
#include "config.h"
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>
#include <exception>

using namespace std;

// 截图并拉取照片
void screenCapAndFetch() {
    try {
        // 截取所有显示器
        captureAllMonitors();
        // 向树莓派发送请求
        fetchAndSaveImage();
    } catch (const exception &e) {
        cerr << "Error in screenCapAndFetch: " << e.what() << endl;
    } catch (...) {
        cerr << "Unknown error in screenCapAndFetch!" << endl;
    }
}

int main() {
    // 重定向标准输出到文件
    ofstream log("C:\\Users\\IWMAI\\OneDrive\\Programs\\C\\WillPower\\windows_service\\output.log", std::ios::app);
    cout.rdbuf(log.rdbuf());  // 重定向标准输出到文件
    cerr.rdbuf(log.rdbuf());  // 重定向标准错误到文件

    try {
        // 初始化所有模块
        Config::load("..\\.env");
        initializeDPI();
        setServerAddress("192.168.68.127", 80);

        // 永不退出循环，在有人操纵电脑、并且电脑连接了两个显示器的情况下，每隔30秒截图并拉取照片一次
        EventMonitor monitor;
        while (true) {
            try {
                SYSTEMTIME st;
                GetLocalTime(&st);

                if (st.wSecond % 30 == 0 && monitor.hasMoved() && getMonitorCount() == 2) {
                    cout << "Current time: " << st.wHour << ":" << st.wMinute << ":" << st.wSecond << endl;
                    screenCapAndFetch();
                    cout << "Screen captured and image fetched!" << endl;
                    Sleep(2000); // 休眠2秒，避免过快的截图和拉取照片
                }
                Sleep(500);
            } catch (const exception &e) {
                cerr << "Error in main loop: " << e.what() << endl;
            } catch (...) {
                cerr << "Unknown error in main loop!" << endl;
            }
        }
    } catch (const exception &e) {
        cerr << "Critical error in initialization: " << e.what() << endl;
    } catch (...) {
        cerr << "Unknown critical error in initialization!" << endl;
    }

    return 0;
}
