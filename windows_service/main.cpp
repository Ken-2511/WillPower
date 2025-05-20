#include <cstdlib>
#include <exception>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

#include "cameraCap.h"
#include "config.h"
#include "eventMonitor.h"
#include "multiScreenCap.h"
#include "utils.h"

using namespace std;

// #define DEBUG

// 截图并拉取照片
void screenCapAndFetch() {
  try {
    // 获取当前日期和时间
    wstring date = getDateString();
    wstring time = getTimeString();

    // 获取所有显示器信息
    std::vector<MonitorInfo> monitors = enumerateMonitors();

    // 截取所有显示器
    std::wstring dateFolderScreen = L"D:\\screenCap\\" + date;
    _wmkdir(dateFolderScreen.c_str());  // 如果文件夹已存在，不会报错
    captureAllMonitors(dateFolderScreen, time);

    // 向树莓派发送请求
    std::wstring dateFolderCamera = L"D:\\cameraCap\\" + date;
    _wmkdir(dateFolderCamera.c_str());  // 如果文件夹已存在，不会报错
    wstringstream filePathCamera;
    filePathCamera << dateFolderCamera << L"\\" << time << L".jpg";
    fetchAndSaveImage(filePathCamera.str());
  } catch (const exception &e) {
    cerr << "Error in screenCapAndFetch: " << e.what() << endl;
  } catch (...) {
    cerr << "Unknown error in screenCapAndFetch!" << endl;
  }
}

int main() {
#ifndef DEBUG

  // 重定向标准输出到文件
  ofstream log(
      "C:\\Users\\IWMAI\\OneDrive\\Programs\\C\\WillPower\\windows_"
      "service\\output.log",
      std::ios::app);
  cout.rdbuf(log.rdbuf());  // 重定向标准输出到文件
  cerr.rdbuf(log.rdbuf());  // 重定向标准错误到文件

#endif

  try {
    cout << "Starting the program..." << endl;

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

#ifndef DEBUG

        if (st.wSecond % 30 == 0 && monitor.hasMoved() &&
            getMonitorCount() == 2) {
#else

        if (st.wSecond % 5 == 0) {
          cout << "%5 == 0" << endl;
          if (monitor.hasMoved(5000)) {
            cout << "Mouse moved!" << endl;
            if (getMonitorCount() == 2) {
              cout << "Two monitors detected! It is the time to capture!"
                   << endl;

#endif

          cout << "Current time: " << st.wHour << ":" << st.wMinute << ":"
               << st.wSecond << endl;
          screenCapAndFetch();
          cout << "Screen captured and image fetched!" << endl;
          Sleep(2000);  // 休眠2秒，避免过快的截图和拉取照片

#ifndef DEBUG
        }

#else
            }
          }
        }

#endif

        monitor.update();
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
