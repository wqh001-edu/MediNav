# Windows ↔ Ubuntu 开发流

## 约定

| 机器 | 做什么 | 不做什么 |
|---|---|---|
| Windows | 编辑源码/文档、git push | 不编译 ROS2 |
| Ubuntu 22.04 VM | `make build` / `make sim` / 测试 | 不直接改未提交的实验代码（可改完再同步） |

## 推荐同步：GitHub

```powershell
# Windows
cd D:\MediNav
git add -A
git commit -m "feat: MediNav ROS2 monorepo"
git remote add origin git@github.com:<you>/MediNav.git
git push -u origin main
```

```bash
# Ubuntu VM
sudo apt install -y git
git clone git@github.com:<you>/MediNav.git ~/MediNav
cd ~/MediNav
bash scripts/setup_ubuntu.sh
source /opt/ros/humble/setup.bash
make build
make sim
```

## 虚拟机建议

- 内存 ≥ 8 GB，CPU ≥ 4 核，显存 3D 加速开启（Gazebo）
- 共享文件夹**不要**用来放 `build/`（性能差），clone 到 VM 本地磁盘
- VirtualBox/VMware 均可；NAT + SSH 端口转发便于宿主机访问 RViz 端口（如需）

## 无 GitHub 时的替代

```powershell
# Windows 打包
cd D:\MediNav
git archive -o medinav.zip HEAD
```

VM 内 `unzip` 后同样 `make build`。
