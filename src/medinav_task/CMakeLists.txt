cmake_minimum_required(VERSION 3.8)
project(medinav_task)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/Order.srv"
  "srv/LoadMedicine.srv"
  "msg/MissionStatus.msg"
  "action/Deliver.action"
)

ament_python_install_package(${PROJECT_NAME})

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/task_node
  scripts/order_client
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
