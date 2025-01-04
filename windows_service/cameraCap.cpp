#include "cameraCap.h"

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <direct.h> // 用于创建目录 _wmkdir
#include <thread>
#include <chrono>

#pragma comment(lib, "gdi32.lib") // 链接 GDI 库

using namespace std;

static string gServerAddress;
static int gServerPort;

void setServerAddress(const string& address, int port) {
    gServerAddress = address;
    gServerPort = port;
}

// 构建请求 URL
string buildRequestURL(const string& endpoint, const string& params) {
    stringstream ss;
    ss << "http://" << gServerAddress << ":" << gServerPort << "/" << endpoint;
    if (!params.empty()) {
        ss << "?" << params;
    }
    return ss.str();
}

// 发送 GET 请求
string sendGetRequest(const string& url) {
    string response;
    return response;
}

// 将获取的图片数据存储到文件
void saveImage(const string& imageData, const string& filename) {
    ofstream file(filename, ios::binary);
    file.write(imageData.c_str(), imageData.size());
}

// 获取图片并保存
void fetchAndSaveImage(const string& endpoint, const string& filename) {
    string url = buildRequestURL(endpoint);
    string imageData = sendGetRequest(url);
    if (isValidResponse(imageData)) {
        saveImage(imageData, filename);
    }
}

// 检查请求的响应是否有效
bool isValidResponse(const string& response) {
    return !response.empty();
}
