/**
 * This file converts all the .bmp files to .png format and save them to another location.
 */

#include "../utils.h"
#include <iostream>
#include <string>
#include <list>
#include <windows.h>

using namespace std;

// Declare the listFiles function
std::list<std::wstring> listFiles(const std::wstring& folder, const std::wstring& pattern);
std::list<std::wstring> listFolders(const std::wstring& folder);

int main() {
	wstring bmpFolder = L"E:\\screenCap"; // in this folder are small folders named by date
	wstring pngFolder = L"E:\\screenCapConverted"; // converted png files will be saved here
	list<wstring> folders = listFolders(bmpFolder);
	for (const auto& folder : folders) {
		list<wstring> bmpFiles = listFiles(bmpFolder + L"\\" + folder, L"*.bmp");
		_wmkdir((pngFolder + L"\\" + folder).c_str()); // create folder for converted files
		for (const auto& bmpFile : bmpFiles) {
			wstring bmpFilePath = bmpFolder + L"\\" + folder + L"\\" + bmpFile;
			wstring pngFilePath = pngFolder + L"\\" + folder + L"\\" +
			                      bmpFile.substr(0, bmpFile.find_last_of(L'.')) + L".png";
			string bmpFilePathA(bmpFilePath.begin(), bmpFilePath.end());
			string pngFilePathA(pngFilePath.begin(), pngFilePath.end());
			// check if the target PNG file already exists
			if (GetFileAttributesA(pngFilePathA.c_str()) != INVALID_FILE_ATTRIBUTES) {
				wcout << L"File already exists: " << pngFilePath << endl;
				continue; // skip conversion if file already exists
			}
			if (bmp2png(bmpFilePathA.c_str(), pngFilePathA.c_str())) {
				wcout << L"Converted: " << bmpFilePath << L" to " << pngFilePath << endl;
			} else {
				wcerr << L"Failed to convert: " << bmpFilePath << endl;
			}
		}
	}
}

list<wstring> listFiles(const wstring& folder, const wstring& pattern) {
    list<wstring> files;
    WIN32_FIND_DATAW findFileData;
    HANDLE hFind = FindFirstFileW((folder + L"\\" + pattern).c_str(), &findFileData);

    if (hFind != INVALID_HANDLE_VALUE) {
        do {
            if (!(findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
                files.push_back(findFileData.cFileName);
            }
        } while (FindNextFileW(hFind, &findFileData) != 0);
        FindClose(hFind);
    }
    return files;
}

list<wstring> listFolders(const wstring& folder) {
	list<wstring> folders;
	WIN32_FIND_DATAW findFileData;
	HANDLE hFind = FindFirstFileW((folder + L"\\*").c_str(), &findFileData);

	if (hFind != INVALID_HANDLE_VALUE) {
		do {
			if (findFileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
				if (wcscmp(findFileData.cFileName, L".") != 0 &&
					wcscmp(findFileData.cFileName, L"..") != 0) {
					folders.push_back(findFileData.cFileName);
				}
			}
		} while (FindNextFileW(hFind, &findFileData) != 0);
		FindClose(hFind);
	}
	return folders;
}