#pragma once
#include <string>
#include <map>

class Config {
public:
    static void load(const std::string& filePath = ".env"); // 加载 .env 文件
    static std::string get(const std::string& key, const std::string& defaultValue = ""); // 获取配置项
private:
    static std::map<std::string, std::string> configMap; // 存储配置项的静态成员
};
