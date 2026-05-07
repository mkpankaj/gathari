import pytest

from app.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def test_hash_password_is_not_plaintext():
    pw = "my-secret-password"
    assert hash_password(pw) != pw


def test_hash_password_produces_unique_salts():
    pw = "same-password"
    assert hash_password(pw) != hash_password(pw)


def test_verify_password_correct():
    pw = "correct-horse-battery-staple"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("right-password")
    assert verify_password("wrong-password", hashed) is False


def test_verify_password_empty_string_against_nonempty():
    hashed = hash_password("non-empty")
    assert verify_password("", hashed) is False


# ---------------------------------------------------------------------------
# JWT round-trip
# ---------------------------------------------------------------------------

def test_create_and_decode_token():
    subject = "user123"
    token = create_access_token(subject)
    assert isinstance(token, str)
    assert len(token) > 0
    decoded = decode_access_token(token)
    assert decoded == subject


def test_decode_invalid_token_returns_none():
    assert decode_access_token("not.a.valid.token") is None


def test_decode_empty_string_returns_none():
    assert decode_access_token("") is None


def test_decode_tampered_token_returns_none():
    token = create_access_token("alice")
    tampered = token[:-5] + "XXXXX"
    assert decode_access_token(tampered) is None


def test_tokens_for_different_subjects_differ():
    t1 = create_access_token("user_a")
    t2 = create_access_token("user_b")
    assert t1 != t2
    assert decode_access_token(t1) == "user_a"
    assert decode_access_token(t2) == "user_b"
