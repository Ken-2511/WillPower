#include "cameraCap.h"

#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <curl/curl.h> // 使用 libcurl 实现 HTTP 请求
#include <vector>
#include <map>

using namespace std;

static string gServerAddress;
static int gServerPort = 80; // 默认端口为 80

// 设置服务器地址和端口
void setServerAddress(const string& address, int port) {
    gServerAddress = address;
    gServerPort = port;
}

// 构建请求 URL
string buildRequestURL(const string& endpoint, const map<string, string>& params) {
    stringstream ss;
    ss << "http://" << gServerAddress << ":" << gServerPort << "/" << endpoint;

    // 拼接查询参数
    if (!params.empty()) {
        ss << "?";
        for (auto it = params.begin(); it != params.end(); ++it) {
            if (it != params.begin()) {
                ss << "&";
            }
            ss << it->first << "=" << it->second;
        }
    }

    return ss.str();
}

// libcurl 写入回调函数，用于保存响应内容
size_t WriteCallback(void* contents, size_t size, size_t nmemb, string* userp) {
    size_t totalSize = size * nmemb;
    userp->append((char*)contents, totalSize);
    return totalSize;
}

// 发送 GET 请求
string sendGetRequest(const string& url) {
    CURL* curl = curl_easy_init();
    if (!curl) {
        cerr << "Failed to initialize CURL" << endl;
        return "";
    }

    string response;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

    CURLcode res = curl_easy_perform(curl);
    if (res != CURLE_OK) {
        cerr << "CURL request failed: " << curl_easy_strerror(res) << endl;
        curl_easy_cleanup(curl);
        return "";
    }

    long http_code = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
    curl_easy_cleanup(curl);

    if (http_code != 200) {
        cerr << "HTTP request failed with code: " << http_code << endl;
        return "";
    }

    return response;
}

// 保存图片数据到文件
bool saveImage(const string& imageData, const string& filename) {
    ofstream file(filename, ios::binary);
    if (!file.is_open()) {
        cerr << "Failed to open file: " << filename << endl;
        return false;
    }

    file.write(imageData.c_str(), imageData.size());
    file.close();
    return true;
}

// 获取图片并保存
bool fetchAndSaveImage(const string& endpoint, const string& filename) {
    string url = buildRequestURL(endpoint, {});
    string imageData = sendGetRequest(url);
    if (!isValidResponse(imageData)) {
        cerr << "Invalid response received for URL: " << url << endl;
        return false;
    }

    if (!saveImage(imageData, filename)) {
        cerr << "Failed to save image to file: " << filename << endl;
        return false;
    }

    cout << "Image successfully saved to " << filename << endl;
    return true;
}

// 检查响应是否有效
bool isValidResponse(const string& response) {
    return !response.empty(); // 简单判断，建议根据实际情况扩展
}
