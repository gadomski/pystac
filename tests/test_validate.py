from pystac import Item


def test_validate_item() -> None:
    item = Item("an-id")
    item.validate()
