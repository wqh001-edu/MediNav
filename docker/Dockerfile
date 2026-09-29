# syntax=docker/dockerfile:1
FROM osrf/ros:humble-desktop

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    ros-humble-teleop-twist-keyboard \
    ros-humble-xacro \
    ros-humble-tf2-tools \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-numpy \
    python3-yaml \
    python3-opencv \
    gazebo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws
COPY . /ws/MediNav
RUN bash -c "source /opt/ros/humble/setup.bash && \
    cd /ws/MediNav && rosdep install --from-paths src --ignore-src -r -y && \
    colcon build --symlink-install"

RUN echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc \
 && echo 'source /ws/MediNav/install/setup.bash' >> /root/.bashrc

WORKDIR /ws/MediNav
CMD ["bash"]
