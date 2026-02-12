# Makefile for temp_convert

CXX = g++
CXXFLAGS = -I"../" -I"../" -I"C:/msys64/mingw64/include"
LDFLAGS = -L"C:/Users/IWMAI/vcpkg/installed/x64-windows/lib" -lpng -lz -lgdi32
SOURCES = main.cpp ../utils.cpp
OBJECTS = $(SOURCES:.cpp=.o)
TARGET = temp_convert.exe

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	del /Q *.o *.exe
