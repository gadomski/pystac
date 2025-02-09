from typing import Any

from typing_extensions import Self

from .extension import Extension


class ProjectionExtension(Extension):
    def __init__(self) -> None:
        self.code: str | None = None

    @classmethod
    def get_extension_url(cls: type[Self]) -> str:
        return "https://stac-extensions.github.io/projection/v2.0.0/schema.json"

    def to_dict(self) -> dict[str, Any]:
        d = {}
        if self.code is not None:
            d["proj:code"] = self.code
        return d
