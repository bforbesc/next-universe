"""The curriculum is the baseline: data-driven, course-keyed, never invented."""
import pytest

from app.services.curriculum import VERTICAL_SLICE, get_modules, load_curriculum


def test_default_course_loads():
    course = load_curriculum("python-beginner")
    assert course["course_id"] == "python-beginner"
    assert len(course["modules"]) >= 10


def test_vertical_slice_modules_in_course_order():
    modules = get_modules("python-beginner", VERTICAL_SLICE)
    assert [m["module_id"] for m in modules] == ["variables", "conditionals", "loops"]
    assert [m["order"] for m in modules] == sorted(m["order"] for m in modules)


def test_modules_carry_baseline_content_for_personalization():
    for module in get_modules("python-beginner", VERTICAL_SLICE):
        # The generator transforms this content; it must actually exist.
        assert len(module["explanation"]) > 50
        assert module["learning_objectives"]
        assert module["examples"]
        assert module["exercise_patterns"]


def test_unknown_module_raises():
    with pytest.raises(ValueError, match="warp-drives"):
        get_modules("python-beginner", ["variables", "warp-drives"])


def test_unknown_course_raises():
    with pytest.raises(FileNotFoundError):
        load_curriculum("underwater-basket-weaving")
