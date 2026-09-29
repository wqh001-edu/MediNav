# 真机 Bring-up 步骤

## 0. 前置

- [ ] `docs/hardware/BOM.md` 物料到齐  
- [ ] `electrical.md` 接线完成，急停有效  
- [ ] Ubuntu 22.04 + ROS2 Humble 已装（`scripts/setup_ubuntu.sh`）  
- [ ] 本仓库已编译：`make build`

## 1. 开机

```bash
source /opt/ros/humble/setup.bash
source ~/MediNav/install/setup.bash
ros2 launch medinav_bringup real_robot.launch.py use_sim_time:=false
```

## 2. 检查话题

```bash
ros2 topic hz /scan
ros2 topic hz /imu
ros2 topic hz /odom
ros2 topic echo /battery_state --once
```

期望：scan ≥ 8 Hz，odom ≥ 20 Hz，电池电压合理。

## 3. 开环运动测试

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# 或
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.15}, angular: {z: 0.0}}'
```

- 直线跑 2 m，测偏差  
- 原地转 360°，比 IMU/编码器航向  

**标定写入** `medinav_hardware/config/medibot_hw.yaml`。

## 4. SLAM 建图（真机）

```bash
ros2 launch medinav_navigation slam.launch.py use_sim_time:=false
# 车动一圈后保存
ros2 run nav2_map_server map_saver_cli -f ~/MediNav/maps/real_hospital
```

## 5. 导航

```bash
ros2 launch medinav_navigation navigation.launch.py \
  use_sim_time:=false \
  map:=/home/$USER/MediNav/maps/real_hospital.yaml
```

RViz2 → **2D Pose Estimate** → **2D Goal** 验证。

## 6. 送药任务

```bash
ros2 launch medinav_task task.launch.py auto_load:=false auto_unload:=false
ros2 run medinav_task order_client ward_3
# 到药房后人工触发装载
ros2 service call /medi/load medinav_task/srv/LoadMedicine "{order_id: '', mass_kg: 0.2}"
```

## 7. 仿真 ↔ 真机切换原则

| 仿真 | 真机 | 是否改代码 |
|---|---|---|
| `use_sim_time:=true` | `false` | 仅参数 |
| Gazebo 插件发 scan/imu | 驱动节点发同名话题 | 否 |
| `diff_drive_controller` | MCU 速度环 + odom 节点 | 可共用接口 |
| `auto_load:=true` | `false` + 微动开关 | 参数 |

## 8. 故障速查

| 现象 | 检查 |
|---|---|
| 无 /scan | 雷达串口权限、`dialout` 组、线缆 |
| 车抖/振荡 | 降 PID，查轮胎打滑 |
| 定位漂 | 轮径/轮距标定，IMU 零偏 |
| 导航原地转 | 初始位姿错误，重设 Pose Estimate |
