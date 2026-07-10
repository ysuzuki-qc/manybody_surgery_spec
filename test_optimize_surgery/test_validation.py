
import pytest
from optimize_surgery import ProblemSolution, SolutionBuilder
from optimize_surgery.solution import InvalidFormatError, SurgeryPathDisjointError, \
    LogicalQubitNotConnectedError, LogicalQubitDoubleConnectError, \
    InconsistentInstructionOrderError, SurgeryPathInvalidAllocationError, \
    InvalidQubitAllocationError
from .sample import sample_input1, sample_input2, sample_input3


def test_sample1():
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 1), (3, 1), (4, 1)])
    solution.add_surgery_path(2, [(3, 2), ])
    output_str = solution.dump_str()
    solution = ProblemSolution(sample_input1, output_str)
    solution.validate()


def test_sample2():
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 3), ])
    solution.add_surgery_path(1, [(4, 3), ])
    output_str = solution.dump_str()
    solution = ProblemSolution(sample_input2, output_str)
    solution.validate()


def test_sample3():
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [])
    solution.add_surgery_path(1, [(1, 2), (1, 3)])
    output_str = solution.dump_str()
    solution = ProblemSolution(sample_input3, output_str)
    solution.validate()


def test_with_allocate_sample1():
    solution = SolutionBuilder(flag_qubit_allocate=True)
    solution.add_qubit_allocation((1, 1))
    solution.add_qubit_allocation((2, 1))
    solution.add_surgery_path(1, [(1, 2), (2, 2), ])
    solution.add_surgery_path(2, [])
    output_str = solution.dump_str()
    solution = ProblemSolution(sample_input1, output_str, flag_qubit_allocate=True)
    solution.validate()


def test_with_allocate_sample2():
    solution = SolutionBuilder(flag_qubit_allocate=True)
    solution.add_qubit_allocation((1, 1))
    solution.add_qubit_allocation((1, 2))
    solution.add_qubit_allocation((2, 1))
    solution.add_qubit_allocation((2, 2))
    solution.add_surgery_path(1, [])
    solution.add_surgery_path(1, [])
    output_str = solution.dump_str()
    solution = ProblemSolution(sample_input2, output_str, flag_qubit_allocate=True)
    solution.validate()


def test_with_allocate_sample3():
    solution = SolutionBuilder(flag_qubit_allocate=True)
    solution.add_qubit_allocation((2, 1))
    solution.add_qubit_allocation((1, 1))
    solution.add_qubit_allocation((3, 1))
    solution.add_qubit_allocation((2, 2))
    solution.add_surgery_path(1, [])
    solution.add_surgery_path(1, [])
    output_str = solution.dump_str()
    solution = ProblemSolution(sample_input3, output_str, flag_qubit_allocate=True)
    solution.validate()


def test_invalid_format1():
    output_str = '''\
1
2 0
'''
    with pytest.raises(InvalidFormatError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_invalid_format2():
    output_str = '''\
1 2 0 1
2 0
'''
    with pytest.raises(InvalidFormatError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_invalid_format3():
    output_str = '''\
1 2 0 1 1
2 0
'''
    with pytest.raises(InvalidFormatError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_invalid_format3():
    output_str = '''\
1 0
2 0
3 0
'''
    with pytest.raises(InvalidFormatError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_disjoint_path1():
    '''Path is disjoint'''
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 1), (4, 1)])
    solution.add_surgery_path(2, [(3, 2), ])
    output_str = solution.dump_str()
    with pytest.raises(SurgeryPathDisjointError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_disjoint_path2():
    '''Path is disjoint (while connected using logical qubit)'''
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 1), (3, 1), (3, 2), (4, 1), (5, 2)])
    solution.add_surgery_path(2, [(3, 2), ])
    output_str = solution.dump_str()
    with pytest.raises(SurgeryPathDisjointError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_not_connected():
    '''There is unconnected logical qubit'''
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 1), (3, 1), (3, 2)])
    solution.add_surgery_path(2, [(3, 2), ])
    output_str = solution.dump_str()
    with pytest.raises(LogicalQubitNotConnectedError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_double_connected():
    '''Logical qubit is doubly connected from different directions'''
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 1), (3, 1), (4, 1)])
    solution.add_surgery_path(1, [(3, 2), ])
    output_str = solution.dump_str()
    with pytest.raises(LogicalQubitDoubleConnectError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_not_ordered():
    '''Instruction is not ordered'''
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 1), (3, 1), (4, 1)])
    solution.add_surgery_path(0, [(3, 2), ])
    output_str = solution.dump_str()
    with pytest.raises(InconsistentInstructionOrderError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_invalid_allocation1():
    '''Overlap with logical qubit'''
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 1), (3, 1), (4, 1), (4, 2)])
    solution.add_surgery_path(2, [(3, 2), ])
    output_str = solution.dump_str()
    with pytest.raises(SurgeryPathInvalidAllocationError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_invalid_allocation2():
    '''Overlap with logical qubit'''
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 3), ])
    solution.add_surgery_path(1, [(4, 3), (3, 3), (2, 3)])
    output_str = solution.dump_str()
    with pytest.raises(SurgeryPathInvalidAllocationError):
        solution = ProblemSolution(sample_input2, output_str)
        solution.validate()


def test_invalid_allocation3():
    '''Allocate out of chip'''
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2, 1), (3, 1), (4, 1), (5, 1), (6, 1)])
    solution.add_surgery_path(2, [(3, 2), ])
    output_str = solution.dump_str()
    with pytest.raises(SurgeryPathInvalidAllocationError):
        solution = ProblemSolution(sample_input1, output_str)
        solution.validate()


def test_invalid_qubit_allocation1():
    '''Logical qubits are overlapped'''
    solution = SolutionBuilder(flag_qubit_allocate=True)
    solution.add_surgery_path(1, [(2, 1), (3, 1), (4, 1), (4, 2)])
    solution.add_surgery_path(2, [(3, 2), ])
    solution.add_qubit_allocation((1, 1))
    solution.add_qubit_allocation((1, 1))
    output_str = solution.dump_str()
    with pytest.raises(InvalidQubitAllocationError):
        solution = ProblemSolution(sample_input1, output_str, flag_qubit_allocate=True)
        solution.validate()


def test_invalid_qubit_allocation2():
    '''Logical qubits are out of chip'''
    solution = SolutionBuilder(flag_qubit_allocate=True)
    solution.add_surgery_path(1, [(2, 1), (3, 1), (4, 1), (4, 2)])
    solution.add_surgery_path(2, [(3, 2), ])
    solution.add_qubit_allocation((-1, -1))
    solution.add_qubit_allocation((1, 1))
    output_str = solution.dump_str()
    with pytest.raises(InvalidQubitAllocationError):
        solution = ProblemSolution(sample_input1, output_str, flag_qubit_allocate=True)
        solution.validate()
