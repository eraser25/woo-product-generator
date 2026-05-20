from src.services.ftp_service import FTPImageUploader


def test_ftp_safe_filename_removes_turkish_chars_and_adds_digest():
    uploader = FTPImageUploader(
        host="example.test",
        username="user",
        password="pass",
        public_base_url="https://example.test",
    )

    safe_name = uploader._safe_filename("Kırmızı Ürün Görseli.jpg", b"abc")

    assert safe_name.endswith(".jpg")
    assert safe_name.startswith("kirmizi-urun-gorseli-")
    assert " " not in safe_name


def test_ftp_connection_checks_write_permission_and_url(monkeypatch):
    uploader = FTPImageUploader(
        host="example.test",
        username="user",
        password="pass",
        public_base_url="https://example.test",
    )
    calls = []

    class FakeFtp:
        def cwd(self, part):
            calls.append(("cwd", part))

        def storbinary(self, command, bio):
            calls.append(("store", command, bio.read()))

        def delete(self, filename):
            calls.append(("delete", filename))

        def quit(self):
            calls.append(("quit",))

    monkeypatch.setattr(uploader, "_connect", lambda: FakeFtp())

    result = uploader.test_connection("public_html/wp-content/uploads")

    assert calls[0] == ("cwd", "/")
    assert calls[1:4] == [("cwd", "public_html"), ("cwd", "wp-content"), ("cwd", "uploads")]
    assert calls[4][0] == "store"
    assert calls[5][0] == "delete"
    assert calls[-1] == ("quit",)
    assert result["public_url"].startswith("https://example.test/wp-content/uploads/")
