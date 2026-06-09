"""'Test the tests': every generated mission's reference solution must pass its
own hidden tests in an isolated subprocess before the mission is persisted."""
from app.schemas import HiddenTest
from app.services.code_verify import verify_program


def test_correct_solution_passes():
    ok, error = verify_program(
        "oxygen_level = 100\nship_name = 'Wanderer'",
        [
            HiddenTest(assertion="oxygen_level == 100", description="oxygen restored"),
            HiddenTest(assertion="ship_name == 'Wanderer'", description="ship named"),
        ],
    )
    assert ok, error


def test_wrong_solution_fails_with_test_description():
    ok, error = verify_program(
        "oxygen_level = 50",
        [HiddenTest(assertion="oxygen_level == 100", description="oxygen restored")],
    )
    assert not ok
    assert "oxygen restored" in error


def test_crashing_solution_fails():
    ok, error = verify_program(
        "raise RuntimeError('boom')",
        [HiddenTest(assertion="True", description="anything")],
    )
    assert not ok
    assert "boom" in error


def test_missing_name_in_assertion_fails():
    ok, error = verify_program(
        "x = 1",
        [HiddenTest(assertion="not_defined == 1", description="checks ghost variable")],
    )
    assert not ok


def test_infinite_loop_is_killed_by_timeout():
    ok, error = verify_program(
        "while True:\n    pass",
        [HiddenTest(assertion="True", description="never reached")],
        timeout=1.0,
    )
    assert not ok
    assert "timed out" in error.lower()
