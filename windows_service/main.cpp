#include "cameraCap.h"
#include "eventMonitor.h"
#include "multiScreenCap.h"
#include <iostream>

using namespace std;



int main() {

    cout << "Start!" << endl;

    // 设置服务器地址和端口
    setServerAddress("192.168.68.127", 80);

    // 初始化 DPI 感知
    initializeDPI();

    // 测试显示器数量

    cout << "Done!" << endl;

    return 0;

}