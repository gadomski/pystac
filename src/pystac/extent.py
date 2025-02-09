from __future__ import annotations

from typing import Any

from typing_extensions import Self

from .constants import DEFAULT_BBOX, DEFAULT_INTERVAL


class Extent:
    @classmethod
    def from_dict(cls: type[Self], d: dict[str, Any]) -> Self:
        return cls(**d)

    def __init__(
        self,
        spatial: SpatialExtent | dict[str, Any] | None = None,
        temporal: TemporalExtent | dict[str, Any] | None = None,
    ):
        if spatial is None:
            self.spatial = SpatialExtent()
        elif isinstance(spatial, SpatialExtent):
            self.spatial = spatial
        else:
            self.spatial = SpatialExtent.from_dict(spatial)
        if temporal is None:
            self.temporal = TemporalExtent()
        elif isinstance(temporal, TemporalExtent):
            self.temporal = temporal
        else:
            self.temporal = TemporalExtent.from_dict(temporal)

    def to_dict(self) -> dict[str, Any]:
        return {
            "spatial": self.spatial.to_dict(),
            "temporal": self.temporal.to_dict(),
        }


class SpatialExtent:
    @classmethod
    def from_dict(cls: type[Self], d: dict[str, Any]) -> Self:
        return cls(**d)

    def __init__(self, bbox: list[list[int | float]] | None = None):
        if bbox is None:
            self.bbox = DEFAULT_BBOX
        else:
            self.bbox = bbox

    def to_dict(self) -> dict[str, Any]:
        return {"bbox": self.bbox}


class TemporalExtent:
    @classmethod
    def from_dict(cls: type[Self], d: dict[str, Any]) -> Self:
        return cls(**d)

    def __init__(self, interval: list[list[str | None]] | None = None):
        if interval is None:
            self.interval = DEFAULT_INTERVAL
        else:
            self.interval = interval

    def to_dict(self) -> dict[str, Any]:
        return {"interval": self.interval}
