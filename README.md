# MMX Optimizer

Multi-objective manufacturing expansion optimizer for RoboBrainstorm.

## Overview

MMX (Multi-objective Mixed-integer eXpansion) is a capacity planning and facility expansion optimization engine. It determines the optimal expansion strategy across multiple manufacturing facilities, balancing cost, capacity, and risk.

## Input

The engine accepts:

- **Facilities**: Current capacity and expansion costs per facility
- **Planning Horizon**: 1-10 years
- **Budget Constraint**: Total capital available for expansion
- **Risk Tolerance**: 0.0 (conservative) to 1.0 (aggressive)

## Output

The engine returns:

- **Expansion Plan**: Facility-by-facility expansion recommendations
  - Expansion units
  - Timing (year to execute)
  - Cost per facility
  - Expected ROI
- **Metrics**:
  - Total cost and capacity added
  - Objective score (multi-criteria optimization)
  - Budget utilization
  - Risk coverage

## Example Usage

```python
payload = {
    "data": {
        "columns": ["facility_id", "current_capacity", "expansion_cost_per_unit"],
        "rows": [
            ["FAC-EAST", 5000, 45000],
            ["FAC-WEST", 3000, 55000],
            ["FAC-MID", 4500, 50000],
        ]
    },
    "variables": {
        "planning_horizon": 5,
        "max_total_budget": 5000000,
        "risk_tolerance": 0.80
    }
}

engine = Engine()
result = engine.run(payload)

# Returns expansion plan optimized for the given constraints
```

## Use Cases

- **Capacity Planning**: Determine which facilities to expand and when
- **Budget Allocation**: Optimize capex spending across multiple sites
- **Risk Management**: Balance aggressive growth with conservative safety margins
- **Scenario Analysis**: Test different budget and risk scenarios

## Development

Run tests:
```bash
pytest tests/
```

## Status

- Version: 1.0.0
- Status: Production Ready
- License: Closed Source (RoboBrainstorm Proprietary)
