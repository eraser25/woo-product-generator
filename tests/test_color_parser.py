from src.core.color_parser import ColorParser


def test_color_parser_accepts_turkish_and_ascii_spellings():
    parser = ColorParser()

    assert parser.parse("kırmızı") == {"name": "Kırmızı", "code": "KRM"}
    assert parser.parse("kirmizi") == {"name": "Kırmızı", "code": "KRM"}
    assert parser.parse("yeşil") == {"name": "Yeşil", "code": "YSL"}


def test_color_parser_returns_stable_unknown_code():
    parser = ColorParser()

    assert parser.parse("mor") == {"name": "Mor", "code": "MOR"}
