cmake_minimum_required(VERSION 3.16)
project(gits_delivery_smoke LANGUAGES CXX)
add_executable(delivery_smoke main.cpp)
target_compile_features(delivery_smoke PRIVATE cxx_std_17)
