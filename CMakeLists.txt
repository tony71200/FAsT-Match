cmake_minimum_required(VERSION 3.18)
project(fast_match_python LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCV REQUIRED COMPONENTS core imgproc imgcodecs)
find_package(TBB REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_fast_match
    python/src/bindings.cpp
    FAsT-Match/FAsTMatch.cpp
    FAsT-Match/MatchConfig.cpp
    FAsT-Match/MatchNet.cpp
)

target_include_directories(_fast_match PRIVATE FAsT-Match)
target_link_libraries(_fast_match PRIVATE ${OpenCV_LIBS} TBB::tbb)

install(TARGETS _fast_match DESTINATION fast_match)
