from app.core.security import hash_password, verify_password


def test_verify_password_returns_true_for_correct_password() -> None:
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_verify_password_returns_false_for_wrong_password() -> None:
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("wrong-password", hashed) is False


def test_hash_password_does_not_store_plaintext() -> None:
    password = "correct-horse-battery-staple"
    hashed = hash_password(password)
    assert hashed != password


def test_hash_password_uses_a_random_salt() -> None:
    password = "correct-horse-battery-staple"
    assert hash_password(password) != hash_password(password)
