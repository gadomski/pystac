import json
import urllib.parse
from pathlib import Path

from .errors import PystacError
from .stac_object import STACObject


def read_file(href: str | Path) -> STACObject:
    """Reads a file from a href.

    Uses the default [Reader][pystac.Reader].

    Args:
        href: The href to read

    Returns:
        The STAC object

    Examples:
        >>> item = pystac.read_file("item.json")
    """
    return Reader().read_file(href)


def write_file(stac_object: STACObject) -> None:
    """**DEPRECATED** Writes a STAC object to a file, using its href.

    If the href is not set, this will throw and error.

    Warning:
        This function is deprecated as of v2.0 and will be removed in a future
        version. Use [STACObject.write_file][pystac.STACObject.write_file]
        instead.

    Args:
        stac_object: The STAC object to write


    """


def make_absolute_href(href: str, base: str | None) -> str:
    if urllib.parse.urlparse(href).scheme:
        return href  # TODO file:// schemes

    if base:
        if urllib.parse.urlparse(base).scheme:
            raise NotImplementedError("url joins not implemented yet, should be easy")
        else:
            if base.endswith("/"):  # TODO windoze
                return str((Path(base) / href).resolve(strict=False))
            else:
                return str((Path(base).parent / href).resolve(strict=False))
    else:
        raise NotImplementedError


class Reader:
    def __init__(self) -> None:
        self.writer = Writer()

    def read_file(self, href: str | Path) -> STACObject:
        with open(href) as f:
            d = json.load(f)
        stac_object = STACObject.from_dict(d)
        stac_object.set_reader(self)
        stac_object.set_writer(self.writer)
        stac_object.set_href(str(href))
        return stac_object


class Writer:
    def write_file(
        self, stac_object: STACObject, href: str | Path | None = None
    ) -> None:
        if not href and not (href := stac_object.get_href()):
            raise PystacError(
                "Cannot write a STACObject without a href. Call "
                "`render()` before saving."
            )
        d = stac_object.to_dict()
        path = Path(href)
        path.parent.mkdir(exist_ok=True)
        with open(path, "w") as f:
            json.dump(d, f)
