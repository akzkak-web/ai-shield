from core.versioning import (
    compare,
    is_older,
    parse_version,
    version_in_ranges,
)


def test_parse_basic():
    assert parse_version("0.1.34") is not None
    assert str(parse_version("0.1.34")) == "0.1.34"
    assert str(parse_version("v0.1.34")) == "0.1.34"


def test_parse_prerelease():
    assert parse_version("0.1.34-rc1").pre == ("rc", 1)
    assert parse_version("1.2.3-beta.2").pre == ("b", 2)


def test_parse_invalid_returns_none():
    assert parse_version(None) is None
    assert parse_version("") is None
    assert parse_version("not-a-version") is not None  # degrades to 0


def test_compare_numeric():
    assert compare(parse_version("0.1.33"), parse_version("0.1.34")) == -1
    assert compare(parse_version("0.1.34"), parse_version("0.1.34")) == 0
    assert compare(parse_version("1.0"), parse_version("0.9.9")) == 1


def test_compare_prerelease_less_than_release():
    assert compare(parse_version("0.1.34rc1"), parse_version("0.1.34")) == -1


def test_version_in_ranges():
    v = parse_version("0.1.33")
    assert version_in_ranges(v, ["<0.1.34"]) is True
    assert version_in_ranges(v, [">=0.1.34"]) is False
    assert version_in_ranges(v, ["<0.1.34", ">=0.1.0"]) is True


def test_unknown_version():
    assert version_in_ranges(None, ["<0.1.34"]) is None
    assert is_older(None, "0.1.34") is None


def test_missing_version_parts():
    # "0.1" should compare as less than "0.1.34".
    assert compare(parse_version("0.1"), parse_version("0.1.34")) == -1
