"""
Unit tests for SR QA Engineer Agent Tool

Tests the scenario generation tool that simulates a Senior QA Engineer
providing test requirements for the 9-step MCP tool chain.
"""

import pytest
from agents.tools.sr_qa_engineer import (
    SCENARIOS,
    SITE_KNOWLEDGE,
    _test_get_scenario,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def easy_scenario():
    """Return expected easy scenario."""
    return SCENARIOS["QA-EASY-001"]


@pytest.fixture
def hard_scenario():
    """Return expected hard scenario."""
    return SCENARIOS["QA-HARD-001"]


# =============================================================================
# Test: get_scenario by complexity level
# =============================================================================

class TestGetScenarioByLevel:
    """Test get_scenario with complexity level parameter."""

    @pytest.mark.asyncio
    async def test_get_easy_scenario(self):
        """Should return an easy scenario when level='easy'."""
        result = await _test_get_scenario({"level": "easy"})

        assert "error" not in result
        assert result["complexity"] == "easy"
        assert result["id"].startswith("QA-EASY")
        assert "persona" in result
        assert "requirement" in result
        assert "url" in result

    @pytest.mark.asyncio
    async def test_get_mid_scenario(self):
        """Should return a mid scenario when level='mid'."""
        result = await _test_get_scenario({"level": "mid"})

        assert "error" not in result
        assert result["complexity"] == "mid"
        assert result["id"].startswith("QA-MID")

    @pytest.mark.asyncio
    async def test_get_hard_scenario(self):
        """Should return a hard scenario when level='hard'."""
        result = await _test_get_scenario({"level": "hard"})

        assert "error" not in result
        assert result["complexity"] == "hard"
        assert result["id"].startswith("QA-HARD")

    @pytest.mark.asyncio
    async def test_case_insensitive_level(self):
        """Should handle case-insensitive level input."""
        result_lower = await _test_get_scenario({"level": "easy"})
        result_upper = await _test_get_scenario({"level": "EASY"})
        result_mixed = await _test_get_scenario({"level": "Easy"})

        assert result_lower["id"] == result_upper["id"] == result_mixed["id"]

    @pytest.mark.asyncio
    async def test_invalid_level_returns_error(self):
        """Should return error for invalid level."""
        result = await _test_get_scenario({"level": "invalid"})

        assert "error" in result


# =============================================================================
# Test: get_scenario by specific ID
# =============================================================================

class TestGetScenarioById:
    """Test get_scenario with specific scenario ID."""

    @pytest.mark.asyncio
    async def test_get_by_exact_id(self):
        """Should return exact scenario when ID provided."""
        result = await _test_get_scenario({"level": "QA-EASY-001"})

        assert result["id"] == "QA-EASY-001"
        assert result["name"] == "Valid login with correct credentials"

    @pytest.mark.asyncio
    async def test_get_by_id_case_insensitive(self):
        """Should handle case-insensitive ID input."""
        result = await _test_get_scenario({"level": "qa-hard-001"})

        assert result["id"] == "QA-HARD-001"

    @pytest.mark.asyncio
    async def test_invalid_id_returns_error(self):
        """Should return error for non-existent ID."""
        result = await _test_get_scenario({"level": "QA-FAKE-999"})

        assert "error" in result


# =============================================================================
# Test: Scenario output format
# =============================================================================

class TestScenarioOutputFormat:
    """Test that scenario output matches Step 1 input requirements."""

    @pytest.mark.asyncio
    async def test_output_has_required_fields(self):
        """Should include all required Step 1 fields."""
        result = await _test_get_scenario({"level": "easy"})

        required_fields = [
            "id",
            "persona",
            "requirement",
            "url",
            "complexity",
            "expected_artifacts",
            "validation_points"
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    @pytest.mark.asyncio
    async def test_persona_format(self):
        """Persona should describe user type."""
        result = await _test_get_scenario({"level": "easy"})

        assert isinstance(result["persona"], str)
        assert len(result["persona"]) > 0

    @pytest.mark.asyncio
    async def test_requirement_is_user_story(self):
        """Requirement should be in user story format."""
        result = await _test_get_scenario({"level": "easy"})

        requirement = result["requirement"]
        assert "As a" in requirement or "I want" in requirement

    @pytest.mark.asyncio
    async def test_url_is_valid(self):
        """URL should be valid automationpractice.pl URL."""
        result = await _test_get_scenario({"level": "easy"})

        url = result["url"]
        assert url.startswith("http://www.automationpractice.pl")

    @pytest.mark.asyncio
    async def test_expected_artifacts_is_list(self):
        """Expected artifacts should be a list of file paths."""
        result = await _test_get_scenario({"level": "easy"})

        artifacts = result["expected_artifacts"]
        assert isinstance(artifacts, list)
        assert len(artifacts) > 0
        assert all(isinstance(a, str) for a in artifacts)

    @pytest.mark.asyncio
    async def test_validation_points_have_dd_ids(self):
        """Validation points should reference DD IDs."""
        result = await _test_get_scenario({"level": "easy"})

        points = result["validation_points"]
        assert isinstance(points, list)
        assert len(points) > 0

        for point in points:
            assert "dd_id" in point
            assert point["dd_id"].startswith("DD-")
            assert "check" in point


# =============================================================================
# Test: Site knowledge
# =============================================================================

class TestSiteKnowledge:
    """Test site knowledge data structure."""

    def test_has_base_url(self):
        """Should have base URL for automationpractice.pl."""
        assert "base_url" in SITE_KNOWLEDGE
        assert "automationpractice.pl" in SITE_KNOWLEDGE["base_url"]

    def test_has_pages(self):
        """Should have page definitions."""
        assert "pages" in SITE_KNOWLEDGE
        pages = SITE_KNOWLEDGE["pages"]

        required_pages = ["home", "authentication", "cart"]
        for page in required_pages:
            assert page in pages, f"Missing page: {page}"
            assert "url" in pages[page]

    def test_has_user_types(self):
        """Should define user types."""
        assert "user_types" in SITE_KNOWLEDGE
        assert "registered user" in SITE_KNOWLEDGE["user_types"]
        assert "guest user" in SITE_KNOWLEDGE["user_types"]


# =============================================================================
# Test: Scenario coverage
# =============================================================================

class TestScenarioCoverage:
    """Test that scenarios provide adequate coverage."""

    def test_has_scenarios_for_each_level(self):
        """Should have at least one scenario per complexity level."""
        levels = {"easy": 0, "mid": 0, "hard": 0}

        for scenario in SCENARIOS.values():
            levels[scenario["complexity"]] += 1

        for level, count in levels.items():
            assert count >= 1, f"No scenarios for level: {level}"

    def test_scenario_ids_are_unique(self):
        """All scenario IDs should be unique."""
        ids = [s["id"] for s in SCENARIOS.values()]
        assert len(ids) == len(set(ids)), "Duplicate scenario IDs found"

    def test_hard_scenarios_note_dd21_dd22(self):
        """Hard scenarios should note potential DD-21/DD-22 triggers."""
        hard_scenarios = [s for s in SCENARIOS.values() if s["complexity"] == "hard"]

        for scenario in hard_scenarios:
            validation_dds = [p["dd_id"] for p in scenario["validation_points"]]
            has_complexity_dd = any(dd in ["DD-20", "DD-21", "DD-22"] for dd in validation_dds)
            assert has_complexity_dd, f"Hard scenario {scenario['id']} should reference DD-20/21/22"
