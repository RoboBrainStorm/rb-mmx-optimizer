"""Multi-objective manufacturing expansion optimizer."""
import json
from typing import Any
from datetime import datetime
import statistics


class Engine:
    """Manufacturing expansion optimization engine."""

    def run(self, payload: dict) -> dict:
        """
        Optimize facility expansion strategy.

        payload schema:
        {
            "data": {
                "columns": ["facility_id", "current_capacity", "expansion_cost"],
                "rows": [["FAC-1", 1000, 50000], ...],
                "row_count": n
            },
            "variables": {
                "planning_horizon": 5,
                "max_total_budget": 5000000,
                "risk_tolerance": 0.80
            },
            "constraints": {}
        }
        """
        try:
            # Extract input
            data = payload.get("data", {})
            variables = payload.get("variables", {})

            if not isinstance(data, dict) or "rows" not in data:
                raise ValueError("Invalid data format: expected 'rows' key in data")

            rows = data.get("rows", [])
            if not rows or len(rows) < 2:
                raise ValueError("Insufficient facility data: minimum 2 facilities required")

            # Parse parameters
            planning_horizon = int(variables.get("planning_horizon", 5))
            max_total_budget = float(variables.get("max_total_budget", 5000000))
            risk_tolerance = float(variables.get("risk_tolerance", 0.80))

            # Validate parameters
            if not 1 <= planning_horizon <= 10:
                raise ValueError("planning_horizon must be between 1 and 10 years")
            if max_total_budget <= 0:
                raise ValueError("max_total_budget must be positive")
            if not 0.0 <= risk_tolerance <= 1.0:
                raise ValueError("risk_tolerance must be between 0.0 and 1.0")

            # Parse facilities
            facilities = self._parse_facilities(rows)
            if not facilities:
                raise ValueError("No valid facility data found")

            # Generate expansion plan
            plan = self._optimize_expansion(
                facilities,
                planning_horizon,
                max_total_budget,
                risk_tolerance
            )

            # Calculate metrics
            total_cost = sum(e["cost"] for e in plan["expansions"])
            total_capacity_added = sum(e["expansion_units"] for e in plan["expansions"])
            unmet_demand_risk = 1.0 - risk_tolerance

            return {
                "outputs": {
                    "expansions": plan["expansions"],
                    "total_cost": round(total_cost, 2),
                    "total_capacity_added": round(total_capacity_added, 2),
                    "objective_score": round(plan["score"], 4),
                    "unmet_demand_risk": round(unmet_demand_risk, 4),
                    "scenarios_covered": plan["scenarios_covered"],
                    "budget_utilization": round(total_cost / max_total_budget, 4),
                },
                "metadata": {
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat(),
                    "engine": "mmx-optimizer",
                }
            }
        except Exception as e:
            return {
                "outputs": {
                    "error": str(e),
                    "status": "failed"
                },
                "metadata": {
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            }

    def _parse_facilities(self, rows: list) -> list:
        """Parse facility data from rows."""
        facilities = []
        for row in rows:
            if isinstance(row, (list, tuple)) and len(row) >= 3:
                try:
                    facility = {
                        "facility_id": str(row[0]),
                        "current_capacity": float(row[1]),
                        "expansion_cost_per_unit": float(row[2]),
                    }
                    facilities.append(facility)
                except (ValueError, TypeError):
                    pass
        return facilities

    def _optimize_expansion(self, facilities: list, horizon: int, budget: float, risk_tolerance: float) -> dict:
        """
        Optimize facility expansion using greedy approach.

        This is a simplified greedy algorithm. In production, use scipy.optimize or pulp.
        """
        expansions = []
        remaining_budget = budget
        scenario_coverage = 0

        # Sort facilities by cost-effectiveness (ROI proxy)
        sorted_fac = sorted(
            facilities,
            key=lambda f: f["expansion_cost_per_unit"],
            reverse=False  # Cheaper first
        )

        # Allocate budget based on risk tolerance
        # Higher tolerance = more aggressive expansion
        max_expansion_per_facility = (budget * risk_tolerance) / len(sorted_fac)

        for facility in sorted_fac:
            if remaining_budget <= 0:
                break

            # Determine expansion amount
            # Base expansion plus risk-based adjustment
            base_expansion = min(
                facility["current_capacity"] * 0.5,  # 50% of current
                max_expansion_per_facility / facility["expansion_cost_per_unit"]
            )

            risk_adjusted = base_expansion * (0.5 + risk_tolerance)
            expansion_units = min(
                risk_adjusted,
                remaining_budget / facility["expansion_cost_per_unit"]
            )

            if expansion_units > 0:
                cost = expansion_units * facility["expansion_cost_per_unit"]
                expansion = {
                    "facility_id": facility["facility_id"],
                    "expansion_units": round(expansion_units, 2),
                    "year_to_expand": 1 + int((horizon * (1 - risk_tolerance)) / 2),
                    "cost": round(cost, 2),
                    "expected_roi": round(1.15 + (risk_tolerance * 0.35), 4)  # ROI scales with risk
                }
                expansions.append(expansion)
                remaining_budget -= cost
                scenario_coverage += 1

        # Calculate objective score (higher is better)
        score = self._calculate_objective(expansions, remaining_budget, budget, risk_tolerance)

        return {
            "expansions": expansions,
            "score": score,
            "scenarios_covered": scenario_coverage
        }

    def _calculate_objective(self, expansions: list, remaining: float, total_budget: float, risk: float) -> float:
        """
        Calculate multi-objective score.
        Score = budget_utilization * risk_adjustment * coverage_factor
        """
        budget_util = 1.0 - (remaining / total_budget)
        coverage_factor = len(expansions) / 3.0  # Normalize by typical facility count
        risk_adjustment = 0.5 + (risk * 0.5)  # Scale to [0.5, 1.0]

        score = budget_util * risk_adjustment * min(coverage_factor, 1.0)
        return score
