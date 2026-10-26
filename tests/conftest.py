from pathlib import Path

import pytest

from triage.schema import load_reports, load_scenarios

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def fixture_reports():
    """Hand-written Incident Reports, keyed by fixture id ("F01" ...) from their scenario_id."""
    return {r.scenario_id.removeprefix("S-"): r for r in load_reports(FIXTURES / "reports.jsonl")}


@pytest.fixture(scope="session")
def fixture_labels():
    """Seeded Labels of the fixture Scenarios, keyed by fixture id."""
    return {
        s.scenario_id.removeprefix("S-"): s.label
        for s in load_scenarios(FIXTURES / "scenarios.jsonl")
    }
