from __future__ import annotations
import io
from typing import Callable


class Instruction:
    def __init__(self) -> None:
        """Constructor
        """
        self.target_list: list[int] = []
        self.direction_list: list[str] = []

    def add_target(self, index: int, direction: str) -> None:
        """Add target qubit

        Args:
            index (int): qubit index (1-indexed)
            direction (str): connection direction, "H" or "V"
        """
        assert(direction in ["H", "V"])
        self.target_list.append(index)
        self.direction_list.append(direction)

    def assert_equal(self, instruction: Instruction) -> None:
        """Assert if not equal

        Args:
            instruction (Instruction): comparison target
        """
        # print(self.target_list, instruction.target_list, self.target_list == instruction.target_list)
        # print(self.direction_list, instruction.direction_list, self.direction_list == instruction.direction_list)
        assert(self.target_list == instruction.target_list)
        assert(self.direction_list == instruction.direction_list)


class ProblemInstance:
    def __init__(self) -> None:
        """Constructor
        """
        self.clear()

    def clear(self) -> None:
        """Clear member variables
        """
        self.chip_size: tuple[int] = (0, 0)
        self.qubit_position_list: list[tuple[int]] = []
        self.instruction_list: list[Instruction] = []

    def set_chip_size(self, width: int, height: int) -> None:
        """Set chip size

        Args:
            width (int): chip width
            height (int): chip height
        """
        self.chip_size = (width, height)

    def add_qubit(self, x: int, y: int) -> None:
        """Add qubit positions

        Args:
            x (int): x-position (1-indexed)
            y (int): y-position (1-indexed)
        """
        position = (x, y)
        self.qubit_position_list.append(position)

    def add_instruction(self, instruction: Instruction) -> None:
        """Add instruction

        Args:
            instruction (Instruction): instruction
        """
        self.instruction_list.append(instruction)

    def dump_str(self) -> str:
        """Dump instance as a string

        Returns:
            str: dumped instance
        """
        s = ""
        s += f"{self.chip_size[0]} {self.chip_size[1]} {len(self.qubit_position_list)}\n"
        for qubit_position in self.qubit_position_list:
            assert(len(qubit_position) == 2)
            s += f"{qubit_position[0]} {qubit_position[1]}\n"
            assert(1 <= qubit_position[0] and qubit_position[0] <= self.chip_size[0])
            assert(1 <= qubit_position[1] and qubit_position[1] <= self.chip_size[1])

        s += f"{len(self.instruction_list)}\n"
        for instruction in self.instruction_list:
            target_list_str = list(map(str, instruction.target_list))
            direction_list_str = list(map(str, instruction.direction_list))
            assert(len(target_list_str) == len(direction_list_str))
            assert(len(target_list_str) >= 2)
            s += f"{len(target_list_str)}\n"
            s += " ".join(target_list_str) + "\n"
            s += " ".join(direction_list_str) + "\n"
        return s

    def load_str(self, instance_str: str) -> None:
        """Load instance from string

        Args:
            instance_str (str): instance string

        Raises:
            ValueError: Invalid format
        """
        buffer = io.StringIO(instance_str)
        self.clear()
        get_int_list: Callable[[io.StringIO, ], list[str]] = lambda x: list(map(int, x.readline().strip().split(" ")))
        get_str_list: Callable[[io.StringIO, ], list[str]] = lambda x: list(map(str, x.readline().strip().split(" ")))
        try:
            chip_width, chip_height, num_qubit = get_int_list(buffer)
            self.set_chip_size(chip_width, chip_height)
            for _ in range(num_qubit):
                x, y = get_int_list(buffer)
                self.add_qubit(x, y)

            num_inst,  = get_int_list(buffer)
            for _ in range(num_inst):
                num_target, = get_int_list(buffer)
                target_list = get_int_list(buffer)
                direction_list = get_str_list(buffer)
                assert(len(target_list) == num_target)
                assert(len(direction_list) == num_target)
                instruction = Instruction()
                for pair in zip(target_list, direction_list):
                    instruction.add_target(*pair)
                self.add_instruction(instruction)

        except:
            raise ValueError("Invalid instance str")

    def assert_equal(self, instance: ProblemInstance) -> None:
        """Assert if not equal

        Args:
            instance (ProblemInstance): comparison target
        """
        assert(self.chip_size == instance.chip_size)
        assert(self.qubit_position_list == instance.qubit_position_list)
        assert(len(self.instruction_list) == len(instance.instruction_list))
        for inst1, inst2 in zip(self.instruction_list, instance.instruction_list):
            inst1.assert_equal(inst2)
