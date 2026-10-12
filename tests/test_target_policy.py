import pytest

from core.target_policy import TargetPolicyError, validate_target


def test_loopback_allowed():
    d = validate_target("127.0.0.1")
    assert d.allowed


def test_metadata_rejected():
    d = validate_target("169.254.169.254")
    assert not d.allowed


def test_private_rejected_by_default():
    d = validate_target("192.168.1.10")
    assert not d.allowed


def test_private_allowed_when_enabled():
    d = validate_target("192.168.1.10", allow_private=True)
    assert d.allowed


def test_public_rejected_by_default():
    d = validate_target("8.8.8.8")
    assert not d.allowed


def test_public_allowed_when_explicit():
    d = validate_target("8.8.8.8", allowed_targets=["8.8.8.8"])
    assert d.allowed


def test_url_rejected():
    d = validate_target("http://127.0.0.1")
    assert not d.allowed


def test_hostname_resolution_and_rebinding_guard(monkeypatch):
    import socket

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type=0: [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 0)),
        ],
    )
    d = validate_target("example.local")
    assert not d.allowed


def test_cidr_private_requires_flag():
    assert not validate_target("192.168.1.0/24").allowed
    assert validate_target("192.168.1.0/24", allow_private=True).allowed


def test_ipv6_loopback_allowed():
    assert validate_target("::1").allowed


def test_ipv4_mapped_loopback_allowed():
    assert validate_target("::ffff:127.0.0.1").allowed


def test_ipv4_mapped_metadata_rejected():
    assert not validate_target("::ffff:169.254.169.254").allowed


def test_ipv4_mapped_private_requires_flag():
    assert not validate_target("::ffff:192.168.1.1").allowed
    assert validate_target("::ffff:192.168.1.1", allow_private=True).allowed
