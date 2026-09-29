#!/usr/bin/env python3
"""Real-robot bringup skeleton (no Gazebo).

Expects real drivers to publish: scan, imu, odom, joint_states
and subscribe: cmd_vel (via diff_drive_controller or motor node).
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        Node(
            package='medinav_task',
            executable='task_node',
            name='medi_task',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'auto_load': False,
                'auto_unload': False,
            }],
        ),
        # TODO: include your motor driver / lidar driver launch here
        # IncludeLaunchDescription(... robot_base_driver.launch.py)
    ])
