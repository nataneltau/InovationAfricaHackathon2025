"""
Static data structures for Innovation Africa Hackathon 2025
Contains all static configuration data from the optimization tool supporting data
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set


# ===========================
# ENUMS FOR CONSTANTS
# ===========================

class Country(Enum):
    """Countries where Innovation Africa operates"""
    CAMEROON = "Cameroon"
    MALAWI = "Malawi"
    SOUTH_AFRICA = "South Africa"
    TANZANIA = "Tanzania"
    UGANDA = "Uganda"
    ZAMBIA = "Zambia"


class JobPosition(Enum):
    """Job positions/roles in the organization"""
    FIELD_CIVIL_ENGINEER = "Field Civil Engineer"
    FIELD_ELECTRICAL_ENGINEER = "Field Electrical Engineer"
    FIELD_ELECTRICAL_SPECIALIST = "Field Electrical Specialist"
    FIELD_HYDROGEOLOGIST = "Field Hydrogeologist"
    FIELD_OFFICER = "Field Officer"
    FIELD_TECHNICIAN = "Field Technician"
    FIELD_WATER_ENGINEER = "Field Water Engineer"
    FIELD_WATER_QUALITY_SPECIALIST = "Field Water Quality Specialist"
    SUPERVISOR_HYDRO_WQ = "Supervisor of Hydrogeology and Water Quality Works"
    SUPERVISOR_MAINTENANCE_ELECTRICAL = "Supervisor of Maintenance and Electrical Works"


class TaskType(Enum):
    """Types of tasks"""
    CORRECTIVE = "Corrective"
    PREVENTATIVE_MAINTENANCE = "Preventative Maintenance"
    MONITORING_EVALUATION = "Monitoring and Evaluation"
    WATER_QUALITY_SAMPLES = "Water Quality Samples"


class SeverityLevel(Enum):
    """Severity levels for SLA"""
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"
    WQ_RISK = "WQ Risk"
    WQ_MAJOR = "WQ Major"


class WorkCategory(Enum):
    """Work categories for SLA"""
    ELECTRICAL_WORKS = "Electrical Works"
    WATER_WORKS = "Water Works"
    HYDRO_WORKS = "Hydro Works"
    CIVIL_WORKS = "Civil Works"
    WATER_QUALITY_ECOLI = "Water Quality - E.Coli"
    WATER_QUALITY_CHEMICAL = "Water Quality - Chemical parameters exceed national standard"
    WATER_QUALITY_MICROBIO = "Water Quality - Micro bio"
    WATER_QUALITY_ACCEPTABILITY = "Water Quality - Acceptability/Operation"


# ===========================
# BUSINESS RULES
# ===========================

@dataclass
class BusinessRule:
    """Business rule definition"""
    task_type: str
    rule: str
    timeline: str


BUSINESS_RULES = {
    "task_rules": [
        BusinessRule(TaskType.CORRECTIVE.value, "Per Severity, Per category", "See SLA table"),
        BusinessRule(TaskType.PREVENTATIVE_MAINTENANCE.value, "Tank Clean", "Every 3 years"),
        BusinessRule(TaskType.PREVENTATIVE_MAINTENANCE.value, "Pump Service", "Every 3 years"),
        BusinessRule(TaskType.MONITORING_EVALUATION.value, "Twice a year", "Between 5-7 months difference"),
        BusinessRule(TaskType.WATER_QUALITY_SAMPLES.value, "Twice a year", "At least 3 months difference between samples")
    ],
    "working_hours": {
        "start": "08:00",
        "end": "18:00"
    },
    "working_days": 5,  # days per week
    "max_tasks_per_day": 3
}


# ===========================
# CERTIFICATION MATRIX
# ===========================

# Certification matrix: which positions can perform which task types
CERTIFICATION_MATRIX = {
    JobPosition.FIELD_CIVIL_ENGINEER.value: [
        TaskType.CORRECTIVE.value
    ],
    JobPosition.FIELD_ELECTRICAL_ENGINEER.value: [
        TaskType.CORRECTIVE.value,
        TaskType.PREVENTATIVE_MAINTENANCE.value,
        TaskType.MONITORING_EVALUATION.value
    ],
    JobPosition.FIELD_ELECTRICAL_SPECIALIST.value: [
        TaskType.CORRECTIVE.value,
        TaskType.PREVENTATIVE_MAINTENANCE.value,
        TaskType.MONITORING_EVALUATION.value
    ],
    JobPosition.FIELD_HYDROGEOLOGIST.value: [
        TaskType.CORRECTIVE.value,
        TaskType.PREVENTATIVE_MAINTENANCE.value,
        TaskType.MONITORING_EVALUATION.value
    ],
    JobPosition.FIELD_OFFICER.value: [
        TaskType.CORRECTIVE.value,
        TaskType.PREVENTATIVE_MAINTENANCE.value
    ],
    JobPosition.FIELD_TECHNICIAN.value: [
        TaskType.CORRECTIVE.value,
        TaskType.PREVENTATIVE_MAINTENANCE.value,
        TaskType.MONITORING_EVALUATION.value
    ],
    JobPosition.FIELD_WATER_ENGINEER.value: [
        TaskType.CORRECTIVE.value,
        TaskType.PREVENTATIVE_MAINTENANCE.value,
        TaskType.MONITORING_EVALUATION.value
    ],
    JobPosition.FIELD_WATER_QUALITY_SPECIALIST.value: [
        TaskType.CORRECTIVE.value,
        TaskType.WATER_QUALITY_SAMPLES.value
    ],
    JobPosition.SUPERVISOR_HYDRO_WQ.value: [
        TaskType.WATER_QUALITY_SAMPLES.value
    ],
    JobPosition.SUPERVISOR_MAINTENANCE_ELECTRICAL.value: [
        TaskType.CORRECTIVE.value,
        TaskType.PREVENTATIVE_MAINTENANCE.value,
        TaskType.MONITORING_EVALUATION.value
    ]
}

def _build_certification_matrix_by_task() -> Dict[str, List[str]]:
    """
    Build reverse certification matrix from CERTIFICATION_MATRIX.
    Private function used internally to generate CERTIFICATION_MATRIX_BY_TASK.
    
    Returns:
        Dictionary mapping task types to lists of positions that can perform them
    """
    matrix_by_task: Dict[str, List[str]] = {}
    for position, task_types in CERTIFICATION_MATRIX.items():
        for task_type in task_types:
            if task_type not in matrix_by_task:
                matrix_by_task[task_type] = []
            matrix_by_task[task_type].append(position)
    
    # Sort the lists for consistent output
    for task_type in matrix_by_task:
        matrix_by_task[task_type].sort()
    
    return matrix_by_task

# Reverse certification matrix: which task types can be performed by which positions
# This is automatically built from CERTIFICATION_MATRIX for consistency
CERTIFICATION_MATRIX_BY_TASK = _build_certification_matrix_by_task()


# ===========================
# SERVICE LEVEL AGREEMENTS (SLA)
# ===========================

# SLA in days for each category and severity level
SLA_MATRIX = {
    SeverityLevel.CRITICAL.value: {
        WorkCategory.ELECTRICAL_WORKS.value: 45,
        WorkCategory.WATER_WORKS.value: 45,
        WorkCategory.HYDRO_WORKS.value: 180,
        WorkCategory.CIVIL_WORKS.value: 90
    },
    SeverityLevel.MAJOR.value: {
        WorkCategory.ELECTRICAL_WORKS.value: 90,
        WorkCategory.WATER_WORKS.value: 90,
        WorkCategory.HYDRO_WORKS.value: 180,
        WorkCategory.CIVIL_WORKS.value: 120
    },
    SeverityLevel.MINOR.value: {
        WorkCategory.ELECTRICAL_WORKS.value: 180,
        WorkCategory.WATER_WORKS.value: 180,
        WorkCategory.CIVIL_WORKS.value: 365
    },
    SeverityLevel.WQ_RISK.value: {
        WorkCategory.WATER_QUALITY_ECOLI.value: 45,
        WorkCategory.WATER_QUALITY_CHEMICAL.value: 180
    },
    SeverityLevel.WQ_MAJOR.value: {
        WorkCategory.WATER_QUALITY_MICROBIO.value: 60,
        WorkCategory.WATER_QUALITY_ACCEPTABILITY.value: 180
    }
}


# ===========================
# EMPLOYEE DATA
# ===========================

@dataclass
class Employee:
    """Employee information"""
    name: str
    country: str
    job_position: str


EMPLOYEES = [
    # South Africa
    Employee("KM", Country.SOUTH_AFRICA.value, JobPosition.SUPERVISOR_MAINTENANCE_ELECTRICAL.value),
    Employee("JM", Country.SOUTH_AFRICA.value, JobPosition.SUPERVISOR_HYDRO_WQ.value),
    Employee("ZN", Country.SOUTH_AFRICA.value, JobPosition.FIELD_WATER_QUALITY_SPECIALIST.value),
    Employee("DN", Country.SOUTH_AFRICA.value, JobPosition.FIELD_WATER_ENGINEER.value),
    Employee("MS", Country.SOUTH_AFRICA.value, JobPosition.FIELD_TECHNICIAN.value),
    Employee("KS", Country.SOUTH_AFRICA.value, JobPosition.FIELD_OFFICER.value),
    Employee("MP", Country.SOUTH_AFRICA.value, JobPosition.FIELD_OFFICER.value),
    Employee("NM", Country.SOUTH_AFRICA.value, JobPosition.FIELD_OFFICER.value),
    Employee("EN", Country.SOUTH_AFRICA.value, JobPosition.FIELD_ELECTRICAL_ENGINEER.value),
    Employee("NS", Country.SOUTH_AFRICA.value, JobPosition.FIELD_CIVIL_ENGINEER.value),
    
    # Cameroon
    Employee("HG", Country.CAMEROON.value, JobPosition.FIELD_WATER_QUALITY_SPECIALIST.value),
    Employee("MO", Country.CAMEROON.value, JobPosition.FIELD_WATER_ENGINEER.value),
    Employee("DB", Country.CAMEROON.value, JobPosition.FIELD_OFFICER.value),
    Employee("ML", Country.CAMEROON.value, JobPosition.FIELD_ELECTRICAL_ENGINEER.value),
    Employee("LN", Country.CAMEROON.value, JobPosition.FIELD_CIVIL_ENGINEER.value),
    
    # Tanzania
    Employee("DM", Country.TANZANIA.value, JobPosition.FIELD_WATER_QUALITY_SPECIALIST.value),
    Employee("BB", Country.TANZANIA.value, JobPosition.FIELD_TECHNICIAN.value),
    Employee("MK", Country.TANZANIA.value, JobPosition.FIELD_OFFICER.value),
    Employee("DG", Country.TANZANIA.value, JobPosition.FIELD_OFFICER.value),
    
    # Uganda
    Employee("SA", Country.UGANDA.value, JobPosition.FIELD_WATER_QUALITY_SPECIALIST.value),
    Employee("OI", Country.UGANDA.value, JobPosition.FIELD_WATER_ENGINEER.value),
    Employee("DI", Country.UGANDA.value, JobPosition.FIELD_TECHNICIAN.value),
    Employee("BL", Country.UGANDA.value, JobPosition.FIELD_OFFICER.value),
    Employee("FN", Country.UGANDA.value, JobPosition.FIELD_OFFICER.value),
    Employee("MH", Country.UGANDA.value, JobPosition.FIELD_OFFICER.value),
    Employee("JO", Country.UGANDA.value, JobPosition.FIELD_HYDROGEOLOGIST.value),
    Employee("EW", Country.UGANDA.value, JobPosition.FIELD_ELECTRICAL_ENGINEER.value),
    
    # Zambia
    Employee("CJ", Country.ZAMBIA.value, JobPosition.FIELD_WATER_QUALITY_SPECIALIST.value),
    Employee("AP", Country.ZAMBIA.value, JobPosition.FIELD_OFFICER.value),
    Employee("JM", Country.ZAMBIA.value, JobPosition.FIELD_OFFICER.value),
    Employee("AP", Country.ZAMBIA.value, JobPosition.FIELD_HYDROGEOLOGIST.value),
    Employee("MM", Country.ZAMBIA.value, JobPosition.FIELD_ELECTRICAL_SPECIALIST.value),
    Employee("IN", Country.ZAMBIA.value, JobPosition.FIELD_CIVIL_ENGINEER.value),
    
    # Malawi
    Employee("AR", Country.MALAWI.value, JobPosition.FIELD_WATER_ENGINEER.value),
    Employee("DC", Country.MALAWI.value, JobPosition.FIELD_OFFICER.value),
    Employee("PK", Country.MALAWI.value, JobPosition.FIELD_OFFICER.value),
    Employee("TC", Country.MALAWI.value, JobPosition.FIELD_HYDROGEOLOGIST.value),
    Employee("MG", Country.MALAWI.value, JobPosition.FIELD_ELECTRICAL_ENGINEER.value),
    Employee("RN", Country.MALAWI.value, JobPosition.FIELD_ELECTRICAL_ENGINEER.value),
]

# Helper dictionary for employee lookup by country
EMPLOYEES_BY_COUNTRY: Dict[str, List[Employee]] = {}
for employee in EMPLOYEES:
    if employee.country not in EMPLOYEES_BY_COUNTRY:
        EMPLOYEES_BY_COUNTRY[employee.country] = []
    EMPLOYEES_BY_COUNTRY[employee.country].append(employee)


# ===========================
# VEHICLE/CAR DATA
# ===========================

@dataclass
class VehicleFleet:
    """Vehicle fleet information per country"""
    innovation_africa_cars: int
    rental_cars: int
    total: int


VEHICLE_FLEET = {
    Country.CAMEROON.value: VehicleFleet(2, 2, 4),
    Country.MALAWI.value: VehicleFleet(3, 3, 6),
    Country.SOUTH_AFRICA.value: VehicleFleet(4, 2, 6),
    Country.TANZANIA.value: VehicleFleet(2, 3, 5),
    Country.UGANDA.value: VehicleFleet(4, 2, 6),
    Country.ZAMBIA.value: VehicleFleet(4, 3, 7)
}


# ===========================
# COUNTRY SUMMARY STATISTICS
# ===========================

def get_employee_count_by_position_and_country() -> Dict[str, Dict[str, int]]:
    """
    Returns a nested dictionary with employee counts:
    {position: {country: count}}
    """
    summary = {}
    
    for employee in EMPLOYEES:
        if employee.job_position not in summary:
            summary[employee.job_position] = {}
        
        if employee.country not in summary[employee.job_position]:
            summary[employee.job_position][employee.country] = 0
        
        summary[employee.job_position][employee.country] += 1
    
    return summary


def get_total_employees_by_country() -> Dict[str, int]:
    """Returns total employee count per country"""
    totals = {}
    for country, employees in EMPLOYEES_BY_COUNTRY.items():
        totals[country] = len(employees)
    return totals


# Pre-calculated summary data
EMPLOYEE_SUMMARY = {
    "by_position_and_country": get_employee_count_by_position_and_country(),
    "total_by_country": get_total_employees_by_country(),
    "grand_total": len(EMPLOYEES)
}


# ===========================
# UTILITY FUNCTIONS
# ===========================

def get_sla_days(severity: str, category: str) -> Optional[int]:
    """
    Get SLA days for a given severity and category
    
    Args:
        severity: The severity level (e.g., "Critical", "Major")
        category: The work category (e.g., "Electrical Works")
    
    Returns:
        Number of days for SLA, or None if not found
    """
    if severity in SLA_MATRIX and category in SLA_MATRIX[severity]:
        return SLA_MATRIX[severity][category]
    return None


def get_certified_positions_for_task(task_type: str) -> List[str]:
    """
    Get all job positions certified for a specific task type
    
    Args:
        task_type: The type of task (e.g., "Corrective", "Water Quality Samples")
    
    Returns:
        List of job positions that can perform this task
    """
    # Use the reverse matrix for O(1) lookup instead of O(n) iteration
    return CERTIFICATION_MATRIX_BY_TASK.get(task_type, []).copy()


def get_available_employees_for_task(task_type: str, country: Optional[str] = None) -> List[Employee]:
    """
    Get all employees who can perform a specific task type
    
    Args:
        task_type: The type of task
        country: Optional country filter
    
    Returns:
        List of employees certified for the task
    """
    certified_positions = get_certified_positions_for_task(task_type)
    available_employees = []
    
    employees_to_check = EMPLOYEES
    if country and country in EMPLOYEES_BY_COUNTRY:
        employees_to_check = EMPLOYEES_BY_COUNTRY[country]
    
    for employee in employees_to_check:
        if employee.job_position in certified_positions:
            available_employees.append(employee)
    
    return available_employees


def get_vehicle_availability(country: str) -> Optional[VehicleFleet]:
    """
    Get vehicle fleet information for a country
    
    Args:
        country: Country name
    
    Returns:
        VehicleFleet object or None if country not found
    """
    return VEHICLE_FLEET.get(country)


# ===========================
# CONSTANTS FOR QUICK ACCESS
# ===========================

# All countries as a list
ALL_COUNTRIES = [country.value for country in Country]

# All job positions as a list  
ALL_JOB_POSITIONS = [position.value for position in JobPosition]

# All task types as a list
ALL_TASK_TYPES = [task_type.value for task_type in TaskType]

# Working hours configuration
WORKING_HOURS = BUSINESS_RULES["working_hours"]
WORKING_DAYS_PER_WEEK = BUSINESS_RULES["working_days"]
MAX_TASKS_PER_DAY = BUSINESS_RULES["max_tasks_per_day"]


if __name__ == "__main__":
    # Example usage and testing
    print("Innovation Africa Static Data Module")
    print("=" * 50)
    
    # Example: Get SLA for Critical Electrical Works
    sla_days = get_sla_days(SeverityLevel.CRITICAL.value, WorkCategory.ELECTRICAL_WORKS.value)
    print(f"SLA for Critical Electrical Works: {sla_days} days")
    
    # Example: Get certified positions for Corrective tasks
    positions = get_certified_positions_for_task(TaskType.CORRECTIVE.value)
    print(f"\nPositions certified for Corrective tasks: {positions}")
    
    # Example: Get available employees in Uganda for Water Quality Samples
    employees = get_available_employees_for_task(
        TaskType.WATER_QUALITY_SAMPLES.value, 
        Country.UGANDA.value
    )
    print(f"\nEmployees in Uganda for Water Quality Samples: {[e.name for e in employees]}")
    
    # Example: Get vehicle availability in Zambia
    vehicles = get_vehicle_availability(Country.ZAMBIA.value)
    if vehicles:
        print(f"\nVehicles in Zambia - IA: {vehicles.innovation_africa_cars}, "
              f"Rental: {vehicles.rental_cars}, Total: {vehicles.total}")
    
    # Example: Show employee summary
    print(f"\nTotal employees by country: {EMPLOYEE_SUMMARY['total_by_country']}")
    print(f"Grand total employees: {EMPLOYEE_SUMMARY['grand_total']}")
    
    # Example: Show the reverse certification matrix
    print("\n" + "=" * 50)
    print("Reverse Certification Matrix (Task → Positions)")
    print("=" * 50)
    for task_type, positions in CERTIFICATION_MATRIX_BY_TASK.items():
        print(f"\n{task_type}:")
        for position in positions:
            print(f"  - {position}")
