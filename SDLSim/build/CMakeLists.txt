cmake_minimum_required(VERSION 3.1.0)
project(SDLSIM VERSION 0.1.0 LANGUAGES C CXX)

add_executable(SDLSIM ../src/main.cpp)

# https://stackoverflow.com/a/29871891
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
target_link_libraries(SDLSIM Threads::Threads)
#

# https://stackoverflow.com/questions/62541168/how-to-add-precompiled-headers-in-cmake-for-visual-studio-generator
target_precompile_headers(SDLSIM PRIVATE ../src/cxxopts.hpp)
#

target_link_libraries(SDLSIM SDL2main SDL2 GL)