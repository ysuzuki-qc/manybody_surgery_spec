import numpy as np

from .instance import ProblemInstance, Instruction
from .solution_builder import SolutionBuilder

def generate_sample1() -> ProblemInstance:
    instance = ProblemInstance()
    instance.set_chip_size(5, 3)
    instance.add_qubit(2, 2)
    instance.add_qubit(4, 2)

    instruction = Instruction()
    instruction.add_target(1, "V")
    instruction.add_target(2, "V")
    instance.add_instruction(instruction)

    instruction = Instruction()
    instruction.add_target(1, "H")
    instruction.add_target(2, "H")
    instance.add_instruction(instruction)
    return instance


def generate_sample2() -> ProblemInstance:
    instance = ProblemInstance()
    instance.set_chip_size(5, 5)
    instance.add_qubit(2, 2)
    instance.add_qubit(2, 4)
    instance.add_qubit(4, 2)
    instance.add_qubit(4, 4)

    instruction = Instruction()
    instruction.add_target(1, "V")
    instruction.add_target(2, "V")
    instance.add_instruction(instruction)

    instruction = Instruction()
    instruction.add_target(3, "V")
    instruction.add_target(4, "V")
    instance.add_instruction(instruction)
    return instance


def generate_sample3() -> ProblemInstance:
    instance = ProblemInstance()
    instance.set_chip_size(4, 4)
    instance.add_qubit(2, 2)
    instance.add_qubit(3, 2)
    instance.add_qubit(2, 3)
    instance.add_qubit(3, 3)

    instruction = Instruction()
    instruction.add_target(1, "H")
    instruction.add_target(2, "H")
    instance.add_instruction(instruction)

    instruction = Instruction()
    instruction.add_target(1, "H")
    instruction.add_target(3, "H")
    instance.add_instruction(instruction)
    return instance

def generate_sample_answer1() -> SolutionBuilder:
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2,1), (3,1), (4,1)])
    solution.add_surgery_path(2, [(3,2),])
    return solution

def generate_sample_answer1_with_allocate() -> SolutionBuilder:
    solution = SolutionBuilder(flag_qubit_allocate=True)
    solution.add_qubit_allocation((1, 1))
    solution.add_qubit_allocation((2, 1))
    solution.add_surgery_path(1, [(1, 2), (2, 2), ])
    solution.add_surgery_path(2, [])
    return solution

def generate_sample_answer2() -> SolutionBuilder:
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [(2,3),])
    solution.add_surgery_path(1, [(4,3),])
    return solution

def generate_sample_answer3() -> SolutionBuilder:
    solution = SolutionBuilder()
    solution.add_surgery_path(1, [])
    solution.add_surgery_path(1, [(1,2),(1,3)])
    return solution


def _allocate_grid(instance: ProblemInstance, qubit_width: int, qubit_height: int):
    """Allocate qubit on grid (each even row and column)

    Allocate width x height qubits in sparse grid

    Args:
        instance (ProblemInstance): target instance
        qubit_width (int): num of qubit width
        qubit_height (int): num of qubit height
    """
    for y in range(qubit_width):
        for x in range(qubit_height):
            instance.add_qubit(2+x*2, 2+y*2)
    instance.set_chip_size(2*qubit_width+1, 2*qubit_height+1)


def _allocate_compact_grid(instance: ProblemInstance, qubit_width: int, qubit_height: int):
    """Allocate qubit on grid (four-qubit cells)

    Allocate width x height qubits in compact grid

    Args:
        instance (ProblemInstance): target instance
        qubit_width (int): num of qubit width
        qubit_height (int): num of qubit height
    """
    max_x = 0
    max_y = 0
    for y in range(qubit_width):
        for x in range(qubit_height):
            px = 2 + (x//2)*3 + x%2
            py = 2 + (y//2)*3 + y%2
            instance.add_qubit(px, py)
            max_x = max(max_x, px)
            max_y = max(max_x, py)
    instance.set_chip_size(max_x+1, max_y+1)


def _add_random_instructions(instance: ProblemInstance, num_inst: int, num_target: int, seed: int):
    """Issue surgery instructions for random connection

    Args:
        instance (ProblemInstance): target instance
        num_inst (int): number of instructions
        num_target (int): number of target qubits per each instruction
        seed (int): seed of rng
    """
    num_qubit = len(instance.qubit_position_list)
    assert(num_target <= num_qubit)
    index_list = list(range(1, num_qubit+1))

    state = np.random.default_rng(seed)
    for _ in range(num_inst):
        state.shuffle(index_list)
        direction = state.choice(["V", "H"])
        instruction = Instruction()
        target_list = index_list[:num_target]
        for target in target_list:
            instruction.add_target(target, direction)
        instance.add_instruction(instruction)


def generate_random_instance_on_grid(qubit_width: int, qubit_height: int, num_inst: int, num_target: int, seed: int) -> ProblemInstance:
    """Generate random problem instance for sprase grid

    Args:
        qubit_width (int): qubit width
        qubit_height (int): qubit height
        num_inst (int): number of instructions
        num_target (int): number of target qubits per instruction
        seed (int): seed of instance

    Returns:
        ProblemInstance: generated instance
    """
    instance = ProblemInstance()
    _allocate_grid(instance, qubit_width, qubit_height)
    _add_random_instructions(instance, num_inst, num_target, seed)
    return instance


def generate_random_instance_on_compact_grid(qubit_width: int, qubit_height: int, num_inst: int, num_target: int, seed: int) -> ProblemInstance:
    """Generate random problem instance for compact grid

    Args:
        qubit_width (int): qubit width
        qubit_height (int): qubit height
        num_inst (int): number of instructions
        num_target (int): number of target qubits per instruction
        seed (int): seed of instance

    Returns:
        ProblemInstance: generated instance
    """
    instance = ProblemInstance()
    _allocate_compact_grid(instance, qubit_width, qubit_height)
    _add_random_instructions(instance, num_inst, num_target, seed)
    return instance


def dump_input_file(instance: ProblemInstance, filename: str, check: bool = True) -> None:
    """Dump instance as a file

    Args:
        instance (ProblemInstance): instance
        filename (str): output filename
        check (bool, optional): If true, validate instnace output. Defaults to True.
    """
    dump = instance.dump_str()

    if check:
        check_instance = ProblemInstance()
        check_instance.load_str(dump)
        instance.assert_equal(check_instance)

    with open(filename, "w") as fout:
        fout.write(dump)

    print(f"Dump: {filename}")


def dump_output_file(instance: SolutionBuilder, filename: str) -> None:
    """Dump instance as a file

    Args:
        instance (ProblemInstance): instance
        filename (str): output filename
        check (bool, optional): If true, validate instnace output. Defaults to True.
    """
    dump = instance.dump_str()

    with open(filename, "w") as fout:
        fout.write(dump)

    print(f"Dump: {filename}")

def generate_problem_set() -> None:
    """Generate all problem set
    """
    dump_input_file(generate_sample1(), "sample1.in")
    dump_input_file(generate_sample2(), "sample2.in")
    dump_input_file(generate_sample3(), "sample3.in")

    dump_output_file(generate_sample_answer1(), "sample1.out")
    dump_output_file(generate_sample_answer1_with_allocate(), "sample1_with_allocate.out")
    dump_output_file(generate_sample_answer2(), "sample2.out")
    dump_output_file(generate_sample_answer3(), "sample3.out")

    num_small_instance = 10
    for instance_index in range(num_small_instance):
        qubit_size = 5
        num_target = 2
        num_inst = 100
        seed = instance_index
        instance = generate_random_instance_on_grid(qubit_size, qubit_size, num_inst, num_target, seed)
        dump_input_file(instance, f"small{instance_index+1}.in")

    num_large_instance = 10
    for instance_index in range(num_large_instance):
        qubit_size = 10
        num_target = 4
        num_inst = 1000
        seed = instance_index
        instance = generate_random_instance_on_compact_grid(qubit_size, qubit_size, num_inst, num_target, seed)
        dump_input_file(instance, f"large{instance_index+1}.in")

    
