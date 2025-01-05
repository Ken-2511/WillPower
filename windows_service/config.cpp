#include "config.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

std::map<std::string, std::string> Config::configMap;

void Config::load(const std::string& filePath) {
    std::ifstream file(filePath);
    if (!file.is_open()) {
        std::cerr << "Failed to open .env file: " << filePath << std::endl;
        return;
    }

    std::string line;
    while (std::getline(file, line)) {
        // 忽略空行和注释
        if (line.empty() || line[0] == '#') continue;

        size_t equalPos = line.find('=');
        if (equalPos == std::string::npos) continue;

        std::string key = line.substr(0, equalPos);
        std::string value = line.substr(equalPos + 1);

        configMap[key] = value;
    }

    file.close();
}

std::string Config::get(const std::string& key, const std::string& defaultValue) {
    auto it = configMap.find(key);
    if (it != configMap.end()) {
        return it->second;
    }
    return defaultValue;
}
