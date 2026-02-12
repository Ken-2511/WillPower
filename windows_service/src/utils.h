#pragma once
#include <string>

std::wstring getDateString();

std::wstring getTimeString();

bool bmp2png(const char* bmp_filename, const char* png_filename);