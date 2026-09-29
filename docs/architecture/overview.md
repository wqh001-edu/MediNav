# MediNav 架构说明

## 分层

```text
┌─────────────────────────────────────────────┐
│  场景/业务     scenarios/*.yaml              │
├─────────────────────────────────────────────┤
│  任务编排     medinav_task (状态机/服务)     │
├─────────────────────────────────────────────┤
│  感知         medinav_perception             │
├─────────────────────────────────────────────┤
│  导航         Nav2 + slam_toolbox            │
├─────────────────────────────────────────────┤
│  运动控制     ros2_control diff_drive        │
├─────────────────────────────────────────────┤
│  硬件抽象     Gazebo 插件  |  真机驱动        │
└─────────────────────────────────────────────┘
```

## 关键接口（真机/仿真共用）

| 话题/服务 | 类型 | 方向 | 说明 |
|---|---|---|---|
| `/cmd_vel` 或 controller | geometry_msgs/Twist | 任务→控制 | 速度指令 |
| `/scan` | sensor_msgs/LaserScan | 传感器→Nav2 | 激光 |
| `/imu` | sensor_msgs/Imu | 传感器 | 惯性 |
| `/odom` | nav_msgs/Odometry | 控制→Nav2 | 里程计 |
| `/map` | nav_msgs/OccupancyGrid | SLAM/map_server | 地图 |
| `/medi/order` | medinav_task/srv/Order | 外部→任务 | 下单 |
| `/medi/load` | medinav_task/srv/LoadMedicine | 外部→任务 | 装载确认 |
| `/medi/status` | medinav_task/msg/MissionStatus | 任务→外部 | 状态广播 |
| `/medi/estop` | std_msgs/Bool | 安全 | 急停 |

## 任务状态机

```text
IDLE → TO_PHARMACY → WAIT_LOAD → TO_WARD → WAIT_UNLOAD → RETURNING → DONE
                 ↘ ERROR ↗（超时/导航失败）
```

与 2026 送药小车固件 `fsm` 命名对齐，便于赛题迁移。

## 仿真 vs 真机

唯一差异在**最底层**是否 Gazebo。Nav2 / 任务 / 感知接口不变。

## 坐标系

`map` → `odom` → `base_footprint` → `base_link` → `{lidar,imu,camera}_link`
