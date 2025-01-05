#include "cameraCap.h"
#include "multiScreenCap.h"
#include <iostream>

using namespace std;



int main() {
    // 设置服务器地址和端口
    setServerAddress("192.168.68.127", 80);

    // 初始化 DPI 感知
    initializeDPI();

    // 截取所有显示器并保存
    captureAllMonitors();