"""Semantic POI map: named wards <-> map poses (hospital_mini world)."""

from dataclasses import dataclass
from typing import Dict, Optional

import yaml


@dataclass(frozen=True)
class Pose2D:
    x: float
    y: float
    yaw: float

    def as_tuple(self):
        return (self.x, self.y, self.yaw)


# Defaults matching medinav_gazebo/worlds/hospital_mini.world
DEFAULT_POIS: Dict[str, Pose2D] = {
    # pharmacy is on the east side; robot approaches facing west (-yaw pi)
    'pharmacy': Pose2D(x=4.5, y=0.0, yaw=3.14159),
    'charge_dock': Pose2D(x=6.2, y=0.0, yaw=0.0),
    # ward door poses approach from corridor (y=0) looking north
    'ward_1': Pose2D(x=-2.0, y=0.55, yaw=1.5708),
    'ward_2': Pose2D(x=-4.5, y=0.55, yaw=1.5708),
    'ward_3': Pose2D(x=-7.0, y=0.55, yaw=1.5708),
    'ward_4': Pose2D(x=-9.5, y=0.55, yaw=1.5708),
}


class PoiMap:
    def __init__(self, path: Optional[str] = None):
        self.pois = dict(DEFAULT_POIS)
        if path:
            self.load(path)

    def load(self, path: str) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        for name, p in data.get('pois', {}).items():
            self.pois[name] = Pose2D(float(p['x']), float(p['y']), float(p['yaw']))

    def get(self, name: str) -> Pose2D:
        if name not in self.pois:
            raise KeyError(f'unknown POI: {name}. known={list(self.pois)}')
        return self.pois[name]

    def names(self):
        return list(self.pois.keys())
