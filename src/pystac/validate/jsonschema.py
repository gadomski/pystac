import importlib.resources
import json
import warnings
from typing import Any, Iterator, cast

import httpx
import referencing.retrieval
from jsonschema.validators import Draft7Validator
from referencing import Registry

from ..catalog import Catalog
from ..collection import Collection
from ..errors import PystacWarning
from ..item import Item
from ..stac_object import STACObject
from .base import Validator


class JsonschemaValidator(Validator):
    """A validator using [json-schema](https://json-schema.org/)."""

    def __init__(self) -> None:
        """Creates a new json-schmea validator.

        This fetches many of the common schemas from local storage, so we don't
        have to hit the network for them.
        """

        self._registry = Registry(retrieve=cached_retrieve_via_httpx).with_contents(  # type: ignore
            registry_contents()
        )
        self._schemas: dict[str, dict[str, Any]] = {}

    def validate(self, stac_object: STACObject) -> None:
        if isinstance(stac_object, Item):
            slug = "item"
        elif isinstance(stac_object, Catalog):
            slug = "catalog"
        elif isinstance(stac_object, Collection):
            slug = "collection"
        else:
            raise Exception("unreachable")
        validator = self._get_validator(stac_object.stac_version, slug)
        validator.validate(stac_object.to_dict())

    def _get_validator(self, version: str, slug: str) -> Draft7Validator:
        path = f"stac/v{version}/{slug}.json"
        if path not in self._schemas:
            try:
                self._schemas[path] = read_schema(path)
            except FileNotFoundError:
                uri = f"https://schemas.stacspec.org/v{version}/{slug}-spec/json-schema/{slug}.json"
                warnings.warn(f"Fetching core schema from {uri}", PystacWarning)
                response = httpx.get(uri).raise_for_status()
                response.raise_for_status()
                self._schemas[path] = response.json()
        schema = self._schemas[path]
        return Draft7Validator(schema, registry=self._registry)


@referencing.retrieval.to_cached_resource()
def cached_retrieve_via_httpx(uri: str) -> str:
    return httpx.get(uri).text


def read_schema(path: str) -> dict[str, Any]:
    with (
        importlib.resources.files("pystac.validate.schemas")
        .joinpath(path)
        .open("r") as f
    ):
        return cast(dict[str, Any], json.load(f))


def registry_contents() -> Iterator[tuple[str, dict[str, Any]]]:
    for name in (
        "bands",
        "basics",
        "common",
        "data-values",
        "datetime",
        "instrument",
        "licensing",
        "provider",
    ):
        uri = f"https://schemas.stacspec.org/v1.1.0/item-spec/json-schema/{name}.json"
        path = f"stac/v1.1.0/{name}.json"
        yield uri, read_schema(path)

    for name in (
        "basics",
        "datetime",
        "instrument",
        "licensing",
        "provider",
    ):
        uri = f"https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/{name}.json"
        path = f"stac/v1.0.0/{name}.json"
        yield uri, read_schema(path)

    for name in (
        "Feature",
        "Geometry",
    ):
        uri = f"https://geojson.org/schema/{name}.json"
        path = f"geojson/{name}.json"
        yield uri, read_schema(path)
