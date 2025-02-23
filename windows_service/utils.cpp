#include "utils.h"
#include <iomanip>
#include <windows.h>
#include <sstream>

std::wstring getDateString() {
    SYSTEMTIME st;
    GetLocalTime(&st);

    std::wstringstream ss;
    ss << std::setw(4) << std::setfill(L'0') << st.wYear << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wMonth << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wDay;
    return ss.str();
}

std::wstring getTimeString() {
    SYSTEMTIME st;
    GetLocalTime(&st);

    std::wstringstream ss;
    ss << std::setw(2) << std::setfill(L'0') << st.wHour << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wMinute << L"-"
       << std::setw(2) << std::setfill(L'0') << st.wSecond;
    return ss.str();
}