#include "cameraCap.h"
#include "eventMonitor.h"
#include "multiScreenCap.h"
#include "config.h"
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>

using namespace std;

int main() {

    cout << "Start!" << endl;

    // 加载环境变量
    Config::load("..\\.env");
    // test
    cout << "API Key:" << Config::get("API_KEY") << endl;

    // 设置服务器地址和端口
    setServerAddress("192.168.68.127", 80);

    // 初始化 DPI 感知
    initializeDPI();

    // 测试显示器数量

    cout << "Done!" << endl;

    return 0;

}