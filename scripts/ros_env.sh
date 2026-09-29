#!/usr/bin/env bash
# Source ROS 2 + workspace overlays
set -euo pipefail
if [[ -f /opt/ros/humble/setup.bash ]]; then
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "$ROOT/install/setup.bash" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/install/setup.bash"
fi
exec "$@"
