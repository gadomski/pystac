from pystac import Catalog


def test_same_reader(catalog: Catalog) -> None:
    for child in catalog.get_children():
        assert child.get_reader() is catalog.get_reader()


def test_same_writer(catalog: Catalog) -> None:
    for child in catalog.get_children():
        assert child.get_writer() is catalog.get_writer()
