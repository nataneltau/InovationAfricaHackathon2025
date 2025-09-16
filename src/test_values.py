"""
Test file to demonstrate the robustness of the Values module
"""

from Values import (
    CERTIFICATION_MATRIX,
    CERTIFICATION_MATRIX_BY_TASK,
    _build_certification_matrix_by_task,
    TaskType,
    JobPosition
)

def test_reverse_matrix_function():
    """Test that the reverse matrix function works correctly"""
    print("Testing reverse matrix function...")
    
    # Rebuild the matrix using the function
    rebuilt_matrix = _build_certification_matrix_by_task()
    
    # Verify it matches the module-level matrix
    assert rebuilt_matrix == CERTIFICATION_MATRIX_BY_TASK, "Matrices don't match!"
    print("✓ Function produces same result as module-level matrix")
    
    # Verify all task types are present
    expected_task_types = {TaskType.CORRECTIVE.value, 
                          TaskType.PREVENTATIVE_MAINTENANCE.value,
                          TaskType.MONITORING_EVALUATION.value,
                          TaskType.WATER_QUALITY_SAMPLES.value}
    
    actual_task_types = set(rebuilt_matrix.keys())
    assert actual_task_types == expected_task_types, "Not all task types present!"
    print("✓ All task types are present in reverse matrix")
    
    # Verify sorting
    for task_type, positions in rebuilt_matrix.items():
        assert positions == sorted(positions), f"Positions for {task_type} are not sorted!"
    print("✓ All position lists are properly sorted")
    
    # Verify reverse mapping is correct
    for position, task_types in CERTIFICATION_MATRIX.items():
        for task_type in task_types:
            assert position in rebuilt_matrix[task_type], \
                f"{position} missing from {task_type} in reverse matrix!"
    print("✓ Reverse mapping is complete and correct")
    
    print("\nAll tests passed! The function-based approach is robust.")

if __name__ == "__main__":
    test_reverse_matrix_function()
    
    print("\n" + "="*50)
    print("Example: Direct function usage")
    print("="*50)
    
    # Show that the function can be called directly if needed
    new_matrix = _build_certification_matrix_by_task()
    print(f"\nTask types in dynamically built matrix: {list(new_matrix.keys())}")
    print(f"Number of positions for Corrective tasks: {len(new_matrix['Corrective'])}")
