#include "utils.h"

#include <windows.h>

#include <iomanip>
#include <sstream>

std::wstring getDateString() {
  SYSTEMTIME st;
  GetLocalTime(&st);

  std::wstringstream ss;
  ss << std::setw(4) << std::setfill(L'0') << st.wYear << L"-" << std::setw(2)
     << std::setfill(L'0') << st.wMonth << L"-" << std::setw(2)
     << std::setfill(L'0') << st.wDay;
  return ss.str();
}

std::wstring getTimeString() {
  SYSTEMTIME st;
  GetLocalTime(&st);

  std::wstringstream ss;
  ss << std::setw(2) << std::setfill(L'0') << st.wHour << L"-" << std::setw(2)
     << std::setfill(L'0') << st.wMinute << L"-" << std::setw(2)
     << std::setfill(L'0') << st.wSecond;
  return ss.str();
}

// 用 libpng 写 PNG 文件
#include <png.h>

#include <cstdio>
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

bool bmp2png(const char* bmp_filename, const char* png_filename) {
    int width, height, channels;
    unsigned char* image_data =
        stbi_load(bmp_filename, &width, &height, &channels, 0);
    if (!image_data) return false;

    FILE* fp = fopen(png_filename, "wb");
    if (!fp) {
        stbi_image_free(image_data);
        return false;
    }

    png_structp png_ptr =
        png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    if (!png_ptr) {
        fclose(fp);
        stbi_image_free(image_data);
        return false;
    }

    png_infop info_ptr = png_create_info_struct(png_ptr);
    if (!info_ptr) {
        png_destroy_write_struct(&png_ptr, NULL);
        fclose(fp);
        stbi_image_free(image_data);
        return false;
    }

    if (setjmp(png_jmpbuf(png_ptr))) {
        png_destroy_write_struct(&png_ptr, &info_ptr);
        fclose(fp);
        stbi_image_free(image_data);
        return false;
    }

    png_init_io(png_ptr, fp);

    int color_type = (channels == 3)   ? PNG_COLOR_TYPE_RGB
                     : (channels == 4) ? PNG_COLOR_TYPE_RGBA
                                       : PNG_COLOR_TYPE_GRAY;

    png_set_IHDR(png_ptr, info_ptr, width, height, 8, color_type,
                 PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_BASE,
                 PNG_FILTER_TYPE_BASE);

    png_write_info(png_ptr, info_ptr);

    png_bytep* row_pointers = new png_bytep[height];
    for (int y = 0; y < height; ++y)
        row_pointers[y] = image_data + y * width * channels;

    png_write_image(png_ptr, row_pointers);
    png_write_end(png_ptr, NULL);

    delete[] row_pointers;
    fclose(fp);
    png_destroy_write_struct(&png_ptr, &info_ptr);
    stbi_image_free(image_data);
    return true;
}