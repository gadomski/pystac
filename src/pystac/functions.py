import warnings
from typing import Any

from .constants import DEFAULT_STAC_VERSION
from .stac_object import STACObject


def get_stac_version() -> str:
    """Returns the default STAC version.

    Returns:
        The default STAC version.

    Examples:
        >>> pystac.get_stac_version()
        "1.1.0"
    """
    return DEFAULT_STAC_VERSION


def set_stac_version(version: str) -> None:
    """**DEPRECATED** This function is a no-op and will be removed in a future version

    Warning:
        In pre-v2.0 PySTAC, this function was used to set the global STAC version.
        In PySTAC v2.0 this global capability has been removed — the user should
        use `Container.set_stac_version()` to mutate an entire catalog.
    """
    warnings.warn(
        "This function is deprecated as of PySTAC v2.0 and is no-op. Use "
        "`Catalog.set_stac_version()` or `Collection.set_stac_version()` to set the "
        "STAC version for a collection of values.",
        FutureWarning,
    )


def read_dict(d: dict[str, Any]) -> STACObject:
    """**DEPRECATED** Reads a STAC object from a dictionary.

    Warning:
        This function is deprecated as of PySTAC v2.0 and will be removed in a
        future version. Use [STACObject.from_dict][pystac.STACObject.from_dict] instead.
    """
    return STACObject.from_dict(d)
