# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.16

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/flicker/Desktop/Cpp

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/flicker/Desktop/Cpp/build

# Include any dependencies generated for this target.
include CMakeFiles/OpenGLApp.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/OpenGLApp.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/OpenGLApp.dir/flags.make

CMakeFiles/OpenGLApp.dir/OpenGL.cpp.o: CMakeFiles/OpenGLApp.dir/flags.make
CMakeFiles/OpenGLApp.dir/OpenGL.cpp.o: ../OpenGL.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/flicker/Desktop/Cpp/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/OpenGLApp.dir/OpenGL.cpp.o"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/OpenGLApp.dir/OpenGL.cpp.o -c /home/flicker/Desktop/Cpp/OpenGL.cpp

CMakeFiles/OpenGLApp.dir/OpenGL.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/OpenGLApp.dir/OpenGL.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/flicker/Desktop/Cpp/OpenGL.cpp > CMakeFiles/OpenGLApp.dir/OpenGL.cpp.i

CMakeFiles/OpenGLApp.dir/OpenGL.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/OpenGLApp.dir/OpenGL.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/flicker/Desktop/Cpp/OpenGL.cpp -o CMakeFiles/OpenGLApp.dir/OpenGL.cpp.s

# Object files for target OpenGLApp
OpenGLApp_OBJECTS = \
"CMakeFiles/OpenGLApp.dir/OpenGL.cpp.o"

# External object files for target OpenGLApp
OpenGLApp_EXTERNAL_OBJECTS =

OpenGLApp: CMakeFiles/OpenGLApp.dir/OpenGL.cpp.o
OpenGLApp: CMakeFiles/OpenGLApp.dir/build.make
OpenGLApp: /usr/lib/x86_64-linux-gnu/libglfw.so.3.3
OpenGLApp: /usr/lib/x86_64-linux-gnu/libGLEW.so
OpenGLApp: /usr/lib/x86_64-linux-gnu/libGLX.so
OpenGLApp: /usr/lib/x86_64-linux-gnu/libOpenGL.so
OpenGLApp: CMakeFiles/OpenGLApp.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/flicker/Desktop/Cpp/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable OpenGLApp"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/OpenGLApp.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/OpenGLApp.dir/build: OpenGLApp

.PHONY : CMakeFiles/OpenGLApp.dir/build

CMakeFiles/OpenGLApp.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/OpenGLApp.dir/cmake_clean.cmake
.PHONY : CMakeFiles/OpenGLApp.dir/clean

CMakeFiles/OpenGLApp.dir/depend:
	cd /home/flicker/Desktop/Cpp/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/flicker/Desktop/Cpp /home/flicker/Desktop/Cpp /home/flicker/Desktop/Cpp/build /home/flicker/Desktop/Cpp/build /home/flicker/Desktop/Cpp/build/CMakeFiles/OpenGLApp.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/OpenGLApp.dir/depend
