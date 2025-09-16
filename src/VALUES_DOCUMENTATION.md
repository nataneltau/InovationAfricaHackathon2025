# Values.py Documentation

## Overview
The `Values.py` file contains all static data structures extracted from the Excel file "Optimization Tool - supporting data.xlsx". This module provides a centralized location for all configuration and reference data used throughout the Innovation Africa Hackathon 2025 project.

## Data Structures Implemented

### 1. **Enums for Constants**
- `Country`: All 6 countries where Innovation Africa operates
- `JobPosition`: All 10 job positions/roles in the organization
- `TaskType`: 4 types of tasks (Corrective, Preventative Maintenance, Monitoring & Evaluation, Water Quality Samples)
- `SeverityLevel`: 5 severity levels for SLA (Critical, Major, Minor, WQ Risk, WQ Major)
- `WorkCategory`: 8 work categories for SLA

### 2. **Business Rules**
- Task rules with timelines
- Working hours (08:00-18:00)
- Working days (5 days per week)
- Maximum tasks per day (3)

### 3. **Certification Matrix**
Two matrices for certification lookups:

**Forward Matrix (CERTIFICATION_MATRIX)**
Maps job positions to their allowed task types:
- Field Civil Engineers → Corrective tasks only
- Field Officers → Corrective and Preventative Maintenance
- Field Water Quality Specialists → Corrective and Water Quality Samples
- And more...

**Reverse Matrix (CERTIFICATION_MATRIX_BY_TASK)**
Maps task types to all positions that can perform them:
- Corrective → 9 positions (all except Supervisor of Hydro/WQ)
- Preventative Maintenance → 7 positions
- Monitoring & Evaluation → 6 positions  
- Water Quality Samples → 2 positions (specialists only)

### 4. **SLA Matrix**
Service Level Agreement days organized by:
- Severity Level (Critical, Major, Minor, WQ Risk, WQ Major)
- Work Category (Electrical, Water, Civil, Hydro, Water Quality)

Examples:
- Critical Electrical Works: 45 days
- Major Civil Works: 120 days
- Minor Water Works: 180 days

### 5. **Employee Data**
39 employees with:
- Name (initials)
- Country assignment
- Job position

Distribution by country:
- South Africa: 10 employees
- Uganda: 8 employees
- Zambia: 6 employees
- Malawi: 6 employees
- Cameroon: 5 employees
- Tanzania: 4 employees

### 6. **Vehicle Fleet Data**
Vehicle availability per country:
- Innovation Africa owned vehicles
- Rental cars
- Total fleet size

Example: Zambia has 4 IA cars + 3 rentals = 7 total vehicles

## Utility Functions

### Core Lookup Functions
```python
# Get SLA days for a specific severity and category
get_sla_days(severity: str, category: str) -> Optional[int]

# Get all positions that can perform a task type
get_certified_positions_for_task(task_type: str) -> List[str]

# Get all employees who can perform a task (with optional country filter)
get_available_employees_for_task(task_type: str, country: Optional[str] = None) -> List[Employee]

# Get vehicle fleet info for a country
get_vehicle_availability(country: str) -> Optional[VehicleFleet]
```

### Pre-calculated Summaries
- `EMPLOYEE_SUMMARY`: Employee counts by position/country and totals
- `EMPLOYEES_BY_COUNTRY`: Quick lookup dictionary for employees by country
- `ALL_COUNTRIES`, `ALL_JOB_POSITIONS`, `ALL_TASK_TYPES`: Lists for iteration

## Usage Examples

### Import the module
```python
from Values import (
    Country, JobPosition, TaskType,
    EMPLOYEES, SLA_MATRIX, VEHICLE_FLEET,
    get_sla_days, get_available_employees_for_task
)
```

### Example 1: Check SLA for a task
```python
days = get_sla_days("Critical", "Electrical Works")
print(f"Must complete within {days} days")  # Output: 45 days
```

### Example 2: Find employees for a task in a specific country
```python
employees = get_available_employees_for_task(
    TaskType.WATER_QUALITY_SAMPLES.value,
    Country.UGANDA.value
)
for emp in employees:
    print(f"{emp.name} - {emp.job_position}")
```

### Example 3: Check vehicle availability
```python
fleet = get_vehicle_availability("South Africa")
if fleet:
    print(f"Total vehicles available: {fleet.total}")
```

### Example 4: Access business rules
```python
from Values import WORKING_HOURS, MAX_TASKS_PER_DAY

print(f"Work starts at {WORKING_HOURS['start']}")
print(f"Maximum {MAX_TASKS_PER_DAY} tasks per day")
```

## Benefits of This Structure

1. **Type Safety**: Uses Enums and dataclasses with type hints
2. **Centralized Data**: Single source of truth for all static data
3. **Easy Maintenance**: Update data in one place
4. **Helper Functions**: Built-in utilities for common queries
5. **Validation**: Enums prevent invalid values
6. **Documentation**: Self-documenting with docstrings and type hints
7. **Testing**: Includes test code in `__main__` block

## Integration with Other Modules

This Values.py module can now be imported and used by:
- `DataFetcher.py` - for validation and constraints
- `DataMapper.py` - for data transformation rules
- `DataBaseConnection.py` - for database constraints
- Any optimization algorithms that need these business rules and constraints

The structured data ensures consistency across the entire application and makes it easy to update business rules without changing code logic.
