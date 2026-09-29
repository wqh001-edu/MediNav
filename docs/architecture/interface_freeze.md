# 接口冻结清单（仿真 = 真机）

业务层（任务/导航）只允许依赖下列接口。改动须走本清单评审。

## 运动

| 名称 | 类型 | 频率 | 说明 |
|---|---|---|---|
| `cmd_vel` / diff_drive cmd | geometry_msgs/Twist | 20 Hz | 线速度 x，角速度 z |
| `odom` | nav_msgs/Odometry | 50 Hz | 里程计 |
| `joint_states` | sensor_msgs/JointState | 50 Hz | 左右轮 |

## 感知

| 名称 | 类型 | 频率 | 说明 |
|---|---|---|---|
| `scan` | sensor_msgs/LaserScan | 10–15 Hz | 2D 雷达，frame=`lidar_link` |
| `imu` | sensor_msgs/Imu | 100 Hz | frame=`imu_link` |
| `camera/image_raw` | sensor_msgs/Image | 15 Hz | 可选 |
| `camera/depth/image_raw` | sensor_msgs/Image | 15 Hz | 深度（可选） |
| `ultrasonic/*` | sensor_msgs/Range | 20 Hz | 6 路近障 |
| `gps/fix` | sensor_msgs/NavSatFix | 5 Hz | 室外扩展 |
| `battery_state` | sensor_msgs/BatteryState | 1 Hz | 真机必填 |
| `/medi/payload/temperature` | sensor_msgs/Temperature | 1 Hz | 药箱 |
| `/medi/payload/humidity` | std_msgs/Float32 | 1 Hz | 药箱 |
| `/medi/payload/present` | std_msgs/Bool | 事件 | 在位开关 |
| `/medi/bumper` | std_msgs/Bool | 事件 | 碰撞 |
| `/medi/sensor_summary` | std_msgs/String | 1 Hz | 聚合健康 |

## 任务 / 安全 / 车队

| 名称 | 类型 | 说明 |
|---|---|---|
| `/medi/order` | `medinav_task/srv/Order` | 下单 |
| `/medi/load` | `medinav_task/srv/LoadMedicine` | 装载确认 |
| `/medi/status` | `medinav_task/msg/MissionStatus` | 状态 |
| `/medi/estop` | `std_msgs/Bool` | 急停 |
| `/medi/digit` | `std_msgs/String` | 门牌数字（mock/相机） |
| `/medi/safety_state` | `std_msgs/String` | 安全状态 |
| `/cmd_vel_nav` → `/cmd_vel` | geometry_msgs/Twist | 安全层拦截 |
| `/medi/fleet_state` | `std_msgs/String` | 双车互斥状态 |

## 坐标系

`map` → `odom` → `base_footprint` → `base_link` → sensors

## 参数同源文件

- `src/medinav_navigation/config/diff_drive_controller.yaml`
- `src/medinav_hardware/config/medibot_hw.yaml`
- `src/medinav_description/urdf/medibot.urdf.xacro`
