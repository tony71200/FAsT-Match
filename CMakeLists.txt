cmake_minimum_required(VERSION 3.18)
project(fast_match_python LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCV REQUIRED COMPONENTS core imgproc imgcodecs)
find_package(TBB REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

set(FAST_MATCH_SOURCES
    FAsT-Match/FAsTMatch.cpp
    FAsT-Match/MatchConfig.cpp
    FAsT-Match/MatchNet.cpp
)

add_library(fast_match_capi SHARED
    FAsT-Match/fast_match_c_api.cpp
    ${FAST_MATCH_SOURCES}
)
target_include_directories(fast_match_capi PRIVATE FAsT-Match)
target_link_libraries(fast_match_capi PRIVATE ${OpenCV_LIBS} TBB::tbb)
set_target_properties(fast_match_capi PROPERTIES OUTPUT_NAME "fast_match_capi")

pybind11_add_module(_fast_match
    python/src/bindings.cpp
    ${FAST_MATCH_SOURCES}
)

target_include_directories(_fast_match PRIVATE FAsT-Match)
target_link_libraries(_fast_match PRIVATE ${OpenCV_LIBS} TBB::tbb)

install(TARGETS _fast_match DESTINATION fast_match)
install(TARGETS fast_match_capi DESTINATION fast_match)
