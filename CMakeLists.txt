cmake_minimum_required(VERSION 3.21)
project(uring_exec LANGUAGES CXX)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

option(URING_EXEC_BUILD_EXAMPLES "Build examples" ON)
option(URING_EXEC_BUILD_TESTS "Build test executables" ON)
option(URING_EXEC_BUILD_BENCHMARKS "Build benchmarks" ON)
option(URING_EXEC_BUILD_ASIO_BENCHMARK "Build Asio benchmark" OFF)
option(URING_EXEC_BUILD_HELLO_CORO "Build the hello_coro example" OFF)

find_package(P2300 CONFIG REQUIRED)
find_package(liburing CONFIG REQUIRED)

add_library(uring_exec INTERFACE)
add_library(uring_exec::uring_exec ALIAS uring_exec)

target_include_directories(uring_exec
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_compile_features(uring_exec INTERFACE cxx_std_20)
target_link_libraries(uring_exec
    INTERFACE
        P2300::P2300
        liburing::liburing
        pthread
)

function(uring_exec_add_target target_name source_file)
    add_executable(${target_name} ${source_file})
    target_link_libraries(${target_name} PRIVATE uring_exec::uring_exec)
endfunction()

if(URING_EXEC_BUILD_EXAMPLES)
    file(GLOB URING_EXEC_EXAMPLE_SOURCES CONFIGURE_DEPENDS examples/*.cpp)
    foreach(source_file IN LISTS URING_EXEC_EXAMPLE_SOURCES)
        get_filename_component(target_name "${source_file}" NAME_WE)
        if(target_name STREQUAL "hello_coro" AND NOT URING_EXEC_BUILD_HELLO_CORO)
            continue()
        endif()
        uring_exec_add_target(${target_name} "${source_file}")
    endforeach()
endif()

if(URING_EXEC_BUILD_TESTS)
    file(GLOB URING_EXEC_TEST_SOURCES CONFIGURE_DEPENDS tests/*.cpp)
    foreach(source_file IN LISTS URING_EXEC_TEST_SOURCES)
        get_filename_component(target_name "${source_file}" NAME_WE)
        uring_exec_add_target(${target_name} "${source_file}")
    endforeach()
endif()

if(URING_EXEC_BUILD_BENCHMARKS)
    set(URING_EXEC_BENCHMARK_SOURCES
        benchmarks/ping.cpp
        benchmarks/ping_when_any.cpp
        benchmarks/pong.cpp
    )
    foreach(source_file IN LISTS URING_EXEC_BENCHMARK_SOURCES)
        get_filename_component(target_name "${source_file}" NAME_WE)
        uring_exec_add_target(${target_name} "${source_file}")
    endforeach()
endif()

if(URING_EXEC_BUILD_BENCHMARKS AND URING_EXEC_BUILD_ASIO_BENCHMARK)
    find_package(asio CONFIG REQUIRED)
    uring_exec_add_target(pong_asio benchmarks/pong_asio.cpp)
    target_compile_definitions(pong_asio PRIVATE ASIO_HAS_IO_URING ASIO_DISABLE_EPOLL)
    target_link_libraries(pong_asio PRIVATE asio::asio)
endif()

install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(TARGETS uring_exec EXPORT uring_execTargets)

install(EXPORT uring_execTargets
    FILE uring_execTargets.cmake
    NAMESPACE uring_exec::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/uring_exec
)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/uring_execConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/uring_execConfig.cmake"
    INSTALL_DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/uring_exec"
)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/uring_execConfigVersion.cmake"
    VERSION "0.1.0"
    COMPATIBILITY SameMajorVersion
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/uring_execConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/uring_execConfigVersion.cmake"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/uring_exec"
)
