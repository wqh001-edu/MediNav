# MediNav ROS2 — 院内送药机器人全栈仿真与硬件落地平台

没有实物也能跑通完整机器人软件栈；有实物后只换硬件接口层。

| 项 | 选择 |
|---|---|
| ROS 2 | Humble Hawksbill |
| 仿真 | Gazebo Classic 11（Humble 官方配套） |
| 导航 | Nav2 + slam_toolbox |
| 任务 | Python 行为编排 + ROS2 Service/Action |
| 控制 | `diff_drive_controller`（ros2_control） |
| 可视化 | RViz2 / Foxglove |
| 目标环境 | Ubuntu 22.04.5 LTS（虚拟机或实体机） |

## 快速开始（Ubuntu 22.04）

```bash
# 1. 系统依赖 + ROS2 Humble（若尚未安装）
bash scripts/setup_ubuntu.sh

# 2. 进入工作区并编译
cd ~/MediNav   # 或你 clone 的路径
make build

# 3. 启动完整仿真（世界 + 机器人 + Nav2 + 任务）
make sim

# 4. 另开终端，发一个送药任务
make order WARD=ward_3
```

## 仓库结构

```
MediNav/
├── src/
│   ├── medinav_description/   # URDF 数字样机（激光/IMU/相机/深度/超声/电池）
│   ├── medinav_gazebo/        # 医院世界、spawn、仿真 launch
│   ├── medinav_navigation/    # Nav2 参数、地图、规划器
│   ├── medinav_task/          # 送药任务状态机 / 服务
│   ├── medinav_perception/    # 门牌识别接口（仿真可 mock）
│   ├── medinav_sensors/       # 传感器注册表、健康监测、超声/货舱环境
│   ├── medinav_safety/        # 急停/碰撞/低电/近障 安全总管
│   ├── medinav_fleet/         # 双车互斥、接力暂停、防撞
│   ├── medinav_mission/       # 多航点任务、rosbag、Foxglove
│   ├── medinav_bringup/       # 一键 bringup（仿真/真机）
│   └── medinav_hardware/      # 真机接口、标定、BOM 对齐
├── scenarios/                 # 任务场景 YAML
├── maps/                      # 栅格地图与语义 POI
├── tools/                     # 评测、扫参、录包
├── scripts/                   # Ubuntu 环境与开发脚本
└── docs/                      # 架构、硬件采购与接线
```

## 传感器与接口一览

| 传感器 | 话题 | 仿真 | 真机驱动建议 |
|---|---|---|---|
| 2D 激光雷达 | `/scan` | Gazebo ray | RPLIDAR / LD19 / YDLidar |
| IMU | `/imu` | Gazebo IMU | BNO055 / MPU6050 |
| 轮式里程计 | `/odom` | diff_drive_controller | MCU 编码器 |
| RGB 相机 | `/camera/image_raw` | Gazebo camera | USB UVC / OpenMV |
| 深度相机 | `/camera/depth/image_raw` | Gazebo depth | RealSense / Astra |
| 超声×6 | `/ultrasonic/{front,rear,fl,fr,rl,rr}` | Gazebo ray | HC-SR04 / VL53L0X |
| GPS（室外扩展） | `/gps/fix` | Gazebo GPS | NEO-M8N |
| 电池 | `/battery_state` | 可 mock | INA219 / MCU ADC |
| 药箱温湿度 | `/medi/payload/temperature` `/humidity` | 模拟 | SHT30 / BME280 |
| 药箱在位 | `/medi/payload/present` | 模拟 | 微动开关 |
| 碰撞 | `/medi/bumper` | 服务触发 | 行程开关 |
| 急停 | `/medi/estop` | 话题 | 硬件自锁 + GPIO |
| 门牌数字 | `/medi/digit` | mock | OpenMV OCR |

完整注册表：`src/medinav_sensors/config/sensor_registry.yaml`。

## 常用命令

```bash
make build          # colcon build
make test           # 单元/集成测试
make sim            # 仿真 + 导航 + 任务 + 传感器 + 安全
make sim-only       # 仅 Gazebo + 机器人
make nav            # 仅导航（已有仿真时）
make map            # SLAM 建图模式
make order WARD=ward_3
make mission        # 多病房巡药
make bag DUR=60     # 录标准 rosbag
make eval           # 跑 scenarios/ 回归
make docker-build   # 可选：容器化环境
```

## 硬件路线（后期购买实物）

文档在 [`docs/hardware/`](docs/hardware/)：

1. `BOM.md` — 推荐/极限两档采购清单
2. `electrical.md` — 电源、电机驱动、传感器接线
3. `mechanical.md` — 底盘尺寸、轮距、安装
4. `bringup_real.md` — 真机上电与接口切换步骤

**原则**：导航与任务层只依赖 ROS2 标准话题（`cmd_vel` / `odom` / `scan` / `imu`），真机接入不改业务代码。

## Windows 开发说明

本仓库在 Windows 侧维护文档、场景与源码，在 Ubuntu 虚拟机内编译运行：

```powershell
# Windows 端仅作编辑与 git 同步；ROS2 不在 Windows 上编译
git clone <this-repo>
# 在 VM 中
git clone <this-repo> ~/MediNav && cd ~/MediNav && make build
```

## 路线图

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M0 | 仓库 / 环境 / 空世界 | ✅ |
| M1 | URDF + ros2_control 开环 | ✅ |
| M2 | 建图 + Nav2 导航 | ✅ |
| M3 | 送药任务状态机 | ✅ |
| M4 | 双车扩展接口 | 🚧 |
| M5 | 评测回归 + 真机文档 | ✅ |

## License

MIT
