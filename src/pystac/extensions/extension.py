from abc import ABC, abstractmethod
from typing import Any

from typing_extensions import Self


class Extension(ABC):
    @classmethod
    @abstractmethod
    def get_extension_url(cls: type[Self]) -> str:
        raise NotImplementedError

    @classmethod
    def is_extension_url(cls: type[Self], url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError
