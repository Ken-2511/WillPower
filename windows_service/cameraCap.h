#pragma once

#include <string>

void setServerAddress(const std::string& address, int port);

// 构建请求 URL
std::string buildRequestURL(const std::string& endpoint, const std::string& params = "");

// 发送 GET 请求
std::string sendGetRequest(const std::string& url);

// 将获取的图片数据存储到文件
void saveImage(const std::string& imageData, const std::string& filename);

// 获取图片并保存
void fetchAndSaveImage(const std::string& endpoint, const std::string& filename);

// 检查请求的响应是否有效
bool isValidResponse(const std::string& response);
