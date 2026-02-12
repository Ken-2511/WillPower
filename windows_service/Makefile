# Makefile for WillPower Windows Service

CXX = g++
CXXFLAGS = -I"C:/Users/IWMAI/vcpkg/installed/x64-windows/include" -I"C:/msys64/mingw64/include"
LDFLAGS = -L"C:/Users/IWMAI/vcpkg/installed/x64-windows/lib" -lcurl -lgdi32 -lpng -lz -mwindows
SRC_DIR = src
DIST_DIR = dist
SOURCES = main.cpp multiScreenCap.cpp cameraCap.cpp eventMonitor.cpp config.cpp utils.cpp
OBJECTS = $(addprefix $(DIST_DIR)/,$(SOURCES:.cpp=.o))
TARGET = $(DIST_DIR)/WillPower.exe
SOURCES_TEST = test.cpp multiScreenCap.cpp cameraCap.cpp eventMonitor.cpp config.cpp utils.cpp
OBJECTS_TEST = $(addprefix $(DIST_DIR)/,$(SOURCES_TEST:.cpp=.o))

all: $(TARGET)

test: $(OBJECTS_TEST)
	$(CXX) $(OBJECTS_TEST) -o $(DIST_DIR)/test.exe $(LDFLAGS)

$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

$(DIST_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	del /Q $(DIST_DIR)\*.o $(DIST_DIR)\*.exe
