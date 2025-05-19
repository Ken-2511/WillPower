# Makefile for WillPower Windows Service

CXX = g++
CXXFLAGS = -I"C:/Users/IWMAI/vcpkg/installed/x64-windows/include" -I"C:/msys64/mingw64/include"
LDFLAGS = -L"C:/Users/IWMAI/vcpkg/installed/x64-windows/lib" -lcurl -lgdi32 -lpng -lz
SOURCES = main.cpp multiScreenCap.cpp cameraCap.cpp eventMonitor.cpp config.cpp utils.cpp
OBJECTS = $(SOURCES:.cpp=.o)
TARGET = WillPower.exe
SOURCES_TEST = test.cpp multiScreenCap.cpp cameraCap.cpp eventMonitor.cpp config.cpp utils.cpp
OBJECTS_TEST = $(SOURCES_TEST:.cpp=.o)

all: $(TARGET)

test: $(OBJECTS_TEST)
	$(CXX) $(OBJECTS_TEST) -o test.exe $(LDFLAGS)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	del /Q *.o *.exe
