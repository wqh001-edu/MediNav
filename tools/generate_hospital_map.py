#!/usr/bin/env python3
"""Generate a simple hospital_mini occupancy grid PGM.

Creates a map roughly matching medinav_gazebo/worlds/hospital_mini.world
so Nav2 can start without SLAM (good enough for first bring-up).
"""
from __future__ import annotations

import os

import numpy as np

# Map metadata must match maps/hospital_mini.yaml
RESOLUTION = 0.05
ORIGIN_X = -11.0
ORIGIN_Y = -4.0
WIDTH_M = 18.0
HEIGHT_M = 8.0


def world_to_map(x: float, y: float, w: int, h: int):
    mx = int((x - ORIGIN_X) / RESOLUTION)
    my = int((y - ORIGIN_Y) / RESOLUTION)
    # PGM row 0 is top; map y increases upward in ROS
    row = h - 1 - my
    col = mx
    return row, col


def fill_box(grid, x0, y0, x1, y1, w, h, value=0):
    for y in np.arange(y0, y1, RESOLUTION):
        for x in np.arange(x0, x1, RESOLUTION):
            r, c = world_to_map(x, y, w, h)
            if 0 <= r < h and 0 <= c < w:
                grid[r, c] = value


def main():
    w = int(WIDTH_M / RESOLUTION)
    h = int(HEIGHT_M / RESOLUTION)
    grid = np.full((h, w), 254, dtype=np.uint8)  # free

    # outer walls (occupied=0)
    fill_box(grid, -11, 1.4, 5, 1.6, w, h, 0)      # north corridor wall
    fill_box(grid, -11, -1.6, 5, -1.4, w, h, 0)    # south
    fill_box(grid, 4.8, -1.6, 5.0, 1.6, w, h, 0)   # east end

    # pharmacy walls
    fill_box(grid, 4.0, 1.1, 5.0, 1.3, w, h, 0)
    fill_box(grid, 4.0, -1.3, 5.0, -1.1, w, h, 0)
    fill_box(grid, 4.9, -1.2, 5.1, 1.2, w, h, 0)

    # ward shells (north side) — leave doorway gaps around y in [0.3, 0.8]
    for cx in (-2.0, -4.5, -7.0, -9.5):
        fill_box(grid, cx - 0.9, 2.2, cx + 0.9, 2.3, w, h, 0)   # back wall
        fill_box(grid, cx - 0.95, 1.4, cx - 0.85, 2.3, w, h, 0)  # left
        fill_box(grid, cx + 0.85, 1.4, cx + 0.95, 2.3, w, h, 0)  # right
        # door jambs
        fill_box(grid, cx - 0.9, 1.4, cx - 0.25, 1.5, w, h, 0)
        fill_box(grid, cx + 0.25, 1.4, cx + 0.9, 1.5, w, h, 0)

    # south obstacles
    fill_box(grid, -4.0, -3.1, -2.0, -1.7, w, h, 0)  # storage
    fill_box(grid, -7.3, -2.8, -5.7, -1.7, w, h, 0)  # nurse

    # write PGM (P5)
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'medinav_navigation', 'maps')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'hospital_mini.pgm')
    with open(path, 'wb') as f:
        f.write(b'P5\n')
        f.write(f'{w} {h}\n'.encode())
        f.write(b'255\n')
        f.write(grid.tobytes())
    print(f'wrote {path} size={w}x{h}')


if __name__ == '__main__':
    main()
