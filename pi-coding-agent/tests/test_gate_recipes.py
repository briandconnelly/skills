"""references/gate-recipes.md examples are copies of fixtures the test suite gates (R7.1)."""

from __future__ import annotations

import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
FIXTURES = SKILL / "tests" / "fixtures" / "gate"
RECIPE = re.compile(r"^Fixture: `tests/fixtures/gate/([^`]+)`\n\n```json\n(.*?)\n```", re.M | re.S)


def _recipes():
    text = (SKILL / "references" / "gate-recipes.md").read_text(encoding="utf-8")
    recipes = RECIPE.findall(text)
    assert recipes, "no recipes found; the pattern or the file changed"
    assert len(recipes) == text.count("Fixture: `"), (
        "a Fixture line is not followed by a JSON block"
    )
    return recipes


def test_every_recipe_equals_its_fixture():
    for path, body in _recipes():
        assert json.loads(body) == json.loads((FIXTURES / path).read_text(encoding="utf-8")), path


def test_every_recipe_is_a_gated_positive_fixture():
    for path, _ in _recipes():
        assert not path.startswith("negative/"), path
        assert path.endswith("gate.json"), path
