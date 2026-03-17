
cmake_minimum_required(VERSION 3.10)
project(VedicKernelsV2 CXX)

set(CMAKE_CXX_STANDARD 11)

add_library(urdhva_sutra SHARED urdhva_sutra.cpp)
add_library(nikhilam_sutra SHARED nikhilam_sutra.cpp)

# Define output directories
set_target_properties(urdhva_sutra PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set_target_properties(nikhilam_sutra PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
