cmake_minimum_required(VERSION 3.8)
project(medinav_perception)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/mock_digit_reader
  scripts/camera_monitor
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
