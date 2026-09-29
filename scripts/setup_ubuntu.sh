#!/usr/bin/env bash
# MediNav — Ubuntu 22.04 + ROS2 Humble bootstrap
set -euo pipefail

echo "==> MediNav Ubuntu 22.04 setup"

if [[ "$(lsb_release -rs)" != "22.04" ]]; then
  echo "WARN: expected Ubuntu 22.04, got $(lsb_release -ds)"
fi

sudo apt-get update
sudo apt-get install -y curl gnupg lsb-release software-properties-common

# --- ROS 2 Humble (desktop) ---
if ! command -v ros2 >/dev/null 2>&1; then
  echo "==> Installing ROS 2 Humble Desktop"
  sudo apt-get install -y locales
  sudo locale-gen en_US en_US.UTF-8
  sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
  export LANG=en_US.UTF-8

  sudo apt-get install -y software-properties-common
  sudo add-apt-repository -y universe

  sudo apt-get update && sudo apt-get install -y curl
  sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
    sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

  sudo apt-get update
  sudo apt-get install -y ros-humble-desktop \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    python3-pip
  sudo rosdep init || true
  rosdep update
else
  echo "==> ROS 2 already present: $(ros2 --version 2>/dev/null || true)"
fi

# --- Gazebo Classic 11 + ros_gz not used on Humble default path ---
echo "==> Installing Gazebo Classic + ROS-Gazebo bridges"
sudo apt-get install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros2-control \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-xacro \
  ros-humble-tf2-tools \
  ros-humble-tf2-ros \
  ros-humble-cv-bridge \
  ros-humble-image-transport \
  ros-humble-message-filters \
  ros-humble-diagnostic-updater \
  ros-humble-teleop-twist-keyboard \
  ros-humble-foxglove-bridge \
  gazebo \
  gazebo-common \
  python3-numpy \
  python3-yaml \
  python3-opencv \
  python3-matplotlib

# --- workspace deps via rosdep (run from repo root) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
if [[ -f "$REPO_ROOT/package.xml" ]] || [[ -d "$REPO_ROOT/src" ]]; then
  echo "==> rosdep install from $REPO_ROOT"
  (cd "$REPO_ROOT" && rosdep install --from-paths src --ignore-src -r -y || true)
fi

echo "==> Done. Next:"
echo "    source /opt/ros/humble/setup.bash"
echo "    cd <MediNav> && make build && make sim"
