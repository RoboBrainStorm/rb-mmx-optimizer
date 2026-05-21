"""Tests for MMX optimization engine."""
import pytest
from engine import Engine


@pytest.fixture
def engine():
    return Engine()


@pytest.fixture
def sample_payload():
    """Sample payload with manufacturing facility data."""
    return {
        "data": {
            "columns": ["facility_id", "current_capacity", "expansion_cost_per_unit"],
            "rows": [
                ["FAC-EAST", 5000, 45000],
                ["FAC-WEST", 3000, 55000],
                ["FAC-MID", 4500, 50000],
                ["FAC-SOUTH", 2000, 60000],
            ],
            "row_count": 4
        },
        "variables": {
            "planning_horizon": 5,
            "max_total_budget": 5000000,
            "risk_tolerance": 0.80
        },
        "constraints": {}
    }


def test_engine_runs_successfully(engine, sample_payload):
    """Test that engine runs without errors."""
    result = engine.run(sample_payload)
    assert "outputs" in result
    assert "metadata" in result
    assert "error" not in result["outputs"]


def test_engine_generates_expansion_plan(engine, sample_payload):
    """Test that engine generates expansion plan."""
    result = engine.run(sample_payload)
    assert "expansions" in result["outputs"]
    assert isinstance(result["outputs"]["expansions"], list)
    assert len(result["outputs"]["expansions"]) > 0


def test_engine_respects_budget(engine, sample_payload):
    """Test that total cost doesn't exceed budget."""
    result = engine.run(sample_payload)
    total_cost = result["outputs"]["total_cost"]
    max_budget = sample_payload["variables"]["max_total_budget"]
    assert total_cost <= max_budget


def test_engine_calculates_metrics(engine, sample_payload):
    """Test that engine calculates all metrics."""
    result = engine.run(sample_payload)
    assert "total_cost" in result["outputs"]
    assert "total_capacity_added" in result["outputs"]
    assert "objective_score" in result["outputs"]
    assert "budget_utilization" in result["outputs"]


def test_engine_handles_insufficient_data(engine):
    """Test that engine rejects insufficient data."""
    payload = {
        "data": {"rows": [["FAC-1", 1000, 50000]], "columns": ["id", "cap", "cost"]},
        "variables": {},
        "constraints": {}
    }
    result = engine.run(payload)
    assert "error" in result["outputs"]


def test_engine_validates_planning_horizon(engine, sample_payload):
    """Test that engine validates planning_horizon."""
    payload = sample_payload.copy()
    payload["variables"]["planning_horizon"] = 15
    result = engine.run(payload)
    assert "error" in result["outputs"]


def test_engine_validates_budget(engine, sample_payload):
    """Test that engine validates max_total_budget."""
    payload = sample_payload.copy()
    payload["variables"]["max_total_budget"] = -1000000
    result = engine.run(payload)
    assert "error" in result["outputs"]
