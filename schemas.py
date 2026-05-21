from pydantic import BaseModel, Field
from typing import List, Optional


class Facility(BaseModel):
    """Production facility specification."""
    facility_id: str
    current_capacity: float = Field(..., description="Current units/month")
    expansion_cost_per_unit: float
    lead_time_months: int
    max_expansion: float = Field(description="Maximum units that can be added")


class DemandScenario(BaseModel):
    """Demand forecast scenario."""
    year: int
    monthly_demand: List[float] = Field(..., description="12 months of demand forecast")
    confidence_level: float = Field(default=0.95)


class OptimizationInput(BaseModel):
    """Input for MMX optimization engine."""
    facilities: List[Facility]
    demand_scenarios: List[DemandScenario]
    planning_horizon: int = Field(default=5, ge=1, le=10, description="Years to plan for")
    max_total_budget: float = Field(description="Total capital available for expansion")
    risk_tolerance: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Risk tolerance (0=conservative, 1=aggressive)"
    )


class ExpansionPlan(BaseModel):
    """Facility expansion decision."""
    facility_id: str
    expansion_units: float
    year_to_expand: int
    cost: float
    expected_roi: float


class OptimizationOutput(BaseModel):
    """Output from MMX optimization."""
    expansions: List[ExpansionPlan]
    total_cost: float
    total_capacity_added: float
    objective_score: float
    unmet_demand_risk: float
    scenarios_covered: int


class SimulationInput(BaseModel):
    """Standard simulation input format."""
    data: dict = Field(description="Dataset from warehouse connector")
    variables: dict = Field(description="User-provided parameters")
    constraints: dict = Field(description="Execution constraints")


class SimulationResult(BaseModel):
    """Standard simulation result format."""
    outputs: dict
