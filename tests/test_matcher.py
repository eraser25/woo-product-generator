from src.core.matcher import ProductMatcher


def test_matcher_returns_sorted_matches_above_threshold():
    matcher = ProductMatcher()

    matches = matcher.find_matches(
        "space cat",
        ["space cat tshirt", "unrelated", "space dog"],
        threshold=0.5,
    )

    assert matches[0]["product"] == "space cat tshirt"
    assert all(item["score"] >= 0.5 for item in matches)
