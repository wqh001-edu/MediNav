cmake_minimum_required(VERSION 3.8)
project(medinav_hardware)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config docs
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
