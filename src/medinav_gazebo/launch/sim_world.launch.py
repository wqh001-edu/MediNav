#!/usr/bin/env python3
"""Launch Gazebo Classic hospital world and spawn MediBot."""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription,
                            RegisterEventHandler, TimerAction)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_gazebo = get_package_share_directory('medinav_gazebo')
    pkg_desc = get_package_share_directory('medinav_description')
    pkg_nav = get_package_share_directory('medinav_navigation')

    world = LaunchConfiguration('world')
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    yaw = LaunchConfiguration('yaw')
    use_sim_time = LaunchConfiguration('use_sim_time')

    controller_yaml = os.path.join(pkg_nav, 'config', 'diff_drive_controller.yaml')

    xacro_file = os.path.join(pkg_desc, 'urdf', 'medibot.urdf.xacro')
    robot_description = ParameterValue(
        Command([
            'xacro ', xacro_file,
            ' controller_yaml:=', controller_yaml,
        ]),
        value_type=str,
    )

    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so',
             '-s', 'libgazebo_ros_init.so', world],
        output='screen',
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }],
        output='screen',
    )

    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'medibot',
            '-topic', 'robot_description',
            '-x', x, '-y', y, '-z', '0.08',
            '-Y', yaw,
        ],
        output='screen',
    )

    # Controllers spawner after spawn_entity exits
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--controller-manager', '/controller_manager'],
        output='screen',
    )
    joint_state_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    delay_diff = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn,
            on_exit=[
                TimerAction(period=2.0, actions=[joint_state_spawner]),
                TimerAction(period=3.5, actions=[diff_drive_spawner]),
            ],
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=os.path.join(pkg_gazebo, 'worlds', 'hospital_mini.world')),
        DeclareLaunchArgument('x', default_value='4.5'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='3.14159'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gazebo,
        robot_state_publisher,
        spawn,
        delay_diff,
    ])
