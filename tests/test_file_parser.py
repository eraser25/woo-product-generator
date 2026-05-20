from src.services.import_service import ImportService


class FakeUpload:
    def __init__(self, name: str, data: bytes = b"image"):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


def test_import_service_groups_files_by_product_name():
    service = ImportService()

    products = service.process_uploaded_files([
        FakeUpload("space_cat_beyaz.jpg"),
        FakeUpload("space_cat_siyah.jpg"),
    ])

    assert len(products) == 1
    assert products[0]["group_key"] == "space_cat"
    assert products[0]["suggested_name"] == "Space Cat"
    assert [c["code"] for c in products[0]["colors"]] == ["BYZ", "SYH"]


def test_import_service_ignores_files_without_color_suffix():
    service = ImportService()

    assert service.process_uploaded_files([FakeUpload("space.jpg")]) == []
