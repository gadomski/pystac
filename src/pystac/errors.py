class PystacError(Exception):
    """A custom error class for this library."""


class StacError(PystacError):
    """A subclass of [PystacError][pystac.PystacError] for errors related to the
    STAC specification itself."""
