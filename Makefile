.PHONY: build clean test sim sim-only nav map order eval mission bag docker-build lint help

WS ?= .
SHELL := /bin/bash

help:
	@echo "MediNav ROS2 Makefile"
	@echo "  make build       - colcon build"
	@echo "  make test        - colcon test + report"
	@echo "  make sim         - full stack (world+robot+nav+task)"
	@echo "  make sim-only    - gazebo + robot only"
	@echo "  make nav         - navigation stack"
	@echo "  make map         - slam mapping mode"
	@echo "  make order       - send order (WARD=ward_3)"
	@echo "  make eval        - run scenario regression"
	@echo "  make mission     - run morning_rounds mission (MISSION=path)"
	@echo "  make bag         - record standard topic bag (DUR=60)"
	@echo "  make clean       - remove build install log"

build:
	colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

clean:
	rm -rf build install log

test:
	colcon test --packages-select medinav_task medinav_navigation
	colcon test-result --verbose

sim:
	ros2 launch medinav_bringup sim_full.launch.py

sim-only:
	ros2 launch medinav_gazebo sim_world.launch.py

nav:
	ros2 launch medinav_navigation navigation.launch.py use_sim_time:=true

map:
	ros2 launch medinav_navigation slam.launch.py

order:
	ros2 service call /medi/order medinav_task/srv/Order "{ward: '$(or $(WARD),ward_3)'}"

eval:
	python3 tools/eval_scenarios.py --scenarios scenarios

mission:
	python3 -m medinav_mission.mission_runner $(or $(MISSION),src/medinav_mission/config/morning_rounds.yaml)

bag:
	ros2 run medinav_mission record_run --duration $(or $(DUR),60)

docker-build:
	docker build -t medinav:humble -f docker/Dockerfile .

lint:
	flake8 src/medinav_task src/medinav_perception tools || true
	xacro src/medinav_description/urdf/medibot.urdf.xacro > /tmp/medibot.urdf
