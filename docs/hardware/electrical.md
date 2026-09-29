# MediBot 电气接线与电源

## 1. 电源树

```
电池 3S/4S (11.1–14.8V)
 ├── 急停开关 → 总正极
 ├── DCDC 12V → 电机驱动 VM
 ├── UBEC 5V/6A → 树莓派 / 雷达 / 传感器
 └── MCU 3.3V (LDO 或板载) → STM32 / IMU
```

**要点**

- 电机电源与逻辑电源单点接地，避免电机回流干扰雷达 USB
- 电池电压进 MCU ADC（分压 1/4）做低压保护
- 急停：切断电机驱动 EN / 总继电器，软件 `/medi/estop` 也要能停

## 2. 电机与驱动

| 信号 | MCU/驱动 | 说明 |
|---|---|---|
| PWM L/R | TIM CH1/CH2 | 20 kHz |
| DIR L/R | GPIO | 方向 |
| ENC A/B | TIM 编码器模式 | 倍频计数 |
| EN 驱动 | GPIO | 急停拉低 |

速度环在 MCU 侧（推荐），ROS 侧发 `cmd_vel` → 串口协议 `V,omega` 或 `vL,vR`。

## 3. 传感器

| 设备 | 接口 | ROS 话题 | frame_id |
|---|---|---|---|
| 激光雷达 | USB-UART | `/scan` | `lidar_link` |
| IMU | I2C/UART | `/imu` | `imu_link` |
| 相机 | USB UVC | `/camera/image_raw` | `camera_link` |
| 深度相机 | USB3 (RealSense) | `/camera/depth/image_raw` | `camera_depth_frame` |
| 超声×6 | GPIO/UART (HC-SR04/VL53L0X) | `/ultrasonic/*` | `ultrasonic_*_link` |
| GPS（可选） | UART | `/gps/fix` | `gps_link` |
| 电池 | ADC / INA219 | `/battery_state` | — |
| 药箱温湿度 | I2C (SHT30/BME280) | `/medi/payload/*` | `payload_link` |
| 药箱微动 | GPIO | `/medi/payload/present` | — |
| 碰撞开关 | GPIO | `/medi/bumper` | — |
| 急停 | GPIO + 硬件切断 | `/medi/estop` | — |

## 4. 串口映射（Ubuntu 实机）

```bash
# 固定 udev 规则示例
KERNEL=="ttyUSB*", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="lidar"
KERNEL=="ttyUSB*", ATTRS{idVendor}=="10c4", SYMLINK+="motor_control"
```

写入 `/etc/udev/rules.d/99-medinav.rules` 后 `sudo udevadm control --reload`。

## 5. 上电顺序

1. 急停复位前检查电机无堵转  
2. 合总开关 → MCU 自检（编码器静止、电压正常）  
3. 树莓派上电 → `real_robot.launch.py`  
4. 确认 `/scan`、`/imu`、`/odom` 有数据后再发导航

## 6. 安全互锁（必须做）

| 条件 | 动作 |
|---|---|
| 急停按下 | 硬件切断电机 + 软件停导航 |
| 电压 < 10.5 V | 减速停车 |
| `/medi/estop` | `cmd_vel=0`，取消 Nav2 goal |
| 碰撞开关 | 立即停 + 状态 ERROR |
