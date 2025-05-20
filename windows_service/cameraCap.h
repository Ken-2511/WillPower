#pragma once

#include <string>
#include <map>

void setServerAddress(const std::string& address, int port);

// 构建请求 URL
std::string buildRequestURL(const std::string& endpoint, const std::map<std::string, std::string>& params);

// 发送 GET 请求
std::string sendGetRequest(const std::string& url);

// 将获取的图片数据存储到文件
bool saveImage(const std::string& imageData, const std::string& filename);

// 获取图片并保存
bool fetchAndSaveImage(const std::string& endpoint, const std::wstring& filename);
bool fetchAndSaveImage(const std::wstring& filename);

// 检查请求的响应是否有效
bool isValidResponse(const std::string& response);
