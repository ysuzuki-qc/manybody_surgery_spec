from collections import defaultdict, deque
from copy import deepcopy
import io
import numpy as np
from .instance import ProblemInstance


class InvalidFormatError(Exception):
    pass


class InvalidQubitAllocationError(Exception):
    pass


class InconsistentInstructionOrderError(Exception):
    pass


class SurgeryPathDisjointError(Exception):
    pass


class SurgeryPathInvalidAllocationError(Exception):
    pass


class LogicalQubitDoubleConnectError(Exception):
    pass


class LogicalQubitNotConnectedError(Exception):
    pass


class SurgeryPath:
    def __init__(self) -> None:
        """Constructor
        """
        self.timing: int = -1
        self.index: int = -1
        self.block_list: list[tuple[int]] = []

    def set_timing(self, timing: int) -> None:
        """Set timing of surgery path

        Args:
            timing (int): _description_
        """
        self.timing = timing

    def set_index(self, index: int) -> None:
        """Set index of this surgery path

        Args:
            index (int): index
        """
        self.index = index

    def add_block(self, x: int, y: int) -> None:
        """Add block to this path

        Args:
            x (int): x-position (1-indexed)
            y (int): y-position (1-indexed)
        """
        self.block_list.append((x, y))

    def is_connected(self) -> bool:
        """Check this path is connected

        Returns:
            bool: True iff it is connected
        """
        if len(self.block_list) == 0:
            return True

        q = deque()
        blocks = self.block_list.copy()
        flags = [0] * len(blocks)
        q.append(blocks[0])
        flags[0] = 1
        while len(q) > 0:
            val = q.popleft()
            neighbors = [
                (val[0]+1, val[1]),
                (val[0]-1, val[1]),
                (val[0], val[1]+1),
                (val[0], val[1]-1),
            ]
            for neighbor in neighbors:
                if neighbor not in self.block_list:
                    continue
                index = self.block_list.index(neighbor)
                if flags[index] == 1:
                    continue
                flags[index] = 1
                q.append(neighbor)
        return all(flags)


class ProblemSolution:
    def __init__(self, input_str: str, output_str: str, flag_qubit_allocate: bool = False) -> None:
        """Constructor

        Args:
            input_str (str): instance string
            output_str (str): answer string
        """
        self.flag_qubit_allocate = flag_qubit_allocate
        self.load_input_str(input_str)
        self.load_output_str(output_str, flag_qubit_allocate)

    def load_input_str(self, input_str: str) -> None:
        """Load input string

        Args:
            input_str (str): input string
        """
        self.instance: ProblemInstance = ProblemInstance()
        self.instance.load_str(input_str)

    def load_output_str(self, output_str: str, flag_qubit_allocate: bool = False) -> None:
        """Load output string

        Args:
            output_str (str): output string

        Raises:
            InvalidFormatError: Format of output string is invalid
        """
        buffer = io.StringIO(output_str)

        # load qubit position list
        num_qubit = len(self.instance.qubit_position_list)
        self.qubit_position_list: list[tuple[int, int]] = [(0, 0)] * num_qubit
        if flag_qubit_allocate:
            for qubit_index in range(num_qubit):
                line = buffer.readline()
                val_list = list(map(int, line.strip().split()))
                if len(val_list) != 2:
                    raise InvalidFormatError("Elements of qubit allocation must be pair of integers")
                qubit_position = (val_list[0], val_list[1])
                self.qubit_position_list[qubit_index] = qubit_position
                qubit_index += 1
        else:
            self.qubit_position_list = self.instance.qubit_position_list

        # load surgery path list
        self.surgery_path_list: list[SurgeryPath] = []
        index = 0
        for line in buffer:
            if len(line.strip()) == 0:
                continue
            surgery_path = SurgeryPath()
            val_list = list(map(int, line.strip().split()))
            if len(val_list) < 2:
                raise InvalidFormatError("Elements of surgery path must be 2 + 2 * block_count")
            timing = val_list[0]
            num_block = val_list[1]
            if not (len(val_list[2:]) == num_block * 2):
                raise InvalidFormatError("Elements of surgery path must be 2 + 2 * block_count")
            pos_x = val_list[2::2]
            pos_y = val_list[3::2]
            surgery_path.set_timing(timing)
            surgery_path.set_index(index)
            index += 1
            for x, y in zip(pos_x, pos_y):
                surgery_path.add_block(x, y)
            self.surgery_path_list.append(surgery_path)

    def get_score(self) -> int:
        """Get score of solution

        Returns:
            int: score
        """
        if len(self.surgery_path_list) == 0:
            return 1
        else:
            return self.surgery_path_list[-1].timing

    def validate(self) -> None:
        """Validate submitted solution

        Raises:
            InvalidFormatError: solution has invalid format
            InconsistentInstructionOrderError: Instruction order is inconsistent
            SurgeryPathDisjointError: Surgery path is disjoint
            SurgeryPathInvalidAllocationError: Surgery path uses invalid blocks
            LogicalQubitNotConnectedError: Logical qubits are not connected by surgery path
            LogicalQubitDoubleConnectError: Logical qubits are connected from different directions at the same timing
        """

        # check qubits are not overlapped and contained in chip
        if self.flag_qubit_allocate:
            if len(set(self.qubit_position_list)) != len(self.qubit_position_list):
                raise InvalidQubitAllocationError("Provided qubit allocations are overlapped")

            for position in self.qubit_position_list:
                is_qubit_contained = \
                    1 <= position[0] and position[0] <= self.instance.chip_size[0] and \
                    1 <= position[1] and position[1] <= self.instance.chip_size[1]
                if not is_qubit_contained:
                    raise InvalidQubitAllocationError("Provided qubit position is out-of-chip")

        # size of surgery paths must be equal to instruction count
        if not (len(self.instance.instruction_list) == len(self.surgery_path_list)):
            raise InvalidFormatError("Inconsistant surgery path lines")

        # timing must be ordered
        last_time = 1
        for surgery_path in self.surgery_path_list:
            if not (last_time <= surgery_path.timing):
                raise InconsistentInstructionOrderError("Surgery path timing is not ordered")
            last_time = surgery_path.timing

        # each surgery path must be connected
        for surgery_path in self.surgery_path_list:
            if not surgery_path.is_connected():
                raise SurgeryPathDisjointError("Surgery path is not connected")

        # each surgery path must be within chip
        for surgery_path in self.surgery_path_list:
            for block in surgery_path.block_list:
                is_block_contained = \
                    1 <= block[0] and block[0] <= self.instance.chip_size[0] and \
                    1 <= block[1] and block[1] <= self.instance.chip_size[1]
                if not is_block_contained:
                    raise SurgeryPathInvalidAllocationError("Block position of surgery path is out-of-chip")

        # each surgery path must not overlap with logical qubits
        for surgery_path in self.surgery_path_list:
            for block in surgery_path.block_list:
                if block in self.qubit_position_list:
                    raise SurgeryPathInvalidAllocationError("Surgery path overlaps on allocated logical qubits")

        # each surgery path must connect targets with appropriate direction
        for instruction, surgery_path in zip(self.instance.instruction_list, self.surgery_path_list):

            # check special case. logical qubits are neighboring, any connection is acceptable
            if len(instruction.target_list) == 2 and instruction.direction_list[0] == instruction.direction_list[1]:
                pos1 = self.qubit_position_list[instruction.target_list[0]-1]
                pos2 = self.qubit_position_list[instruction.target_list[1]-1]
                if instruction.direction_list[0] == "H":
                    if pos2 == (pos1[0]+1, pos1[1]) or pos2 == (pos1[0]-1, pos1[1]):
                        continue
                if instruction.direction_list[0] == "V":
                    if pos2 == (pos1[0], pos1[1]+1) or pos2 == (pos1[0], pos1[1]-1):
                        continue

            for index, direction in zip(instruction.target_list, instruction.direction_list):
                position = self.qubit_position_list[index-1]
                neighbor_list = []
                if direction == "H":
                    neighbor_list.append((position[0]+1, position[1]))
                    neighbor_list.append((position[0]-1, position[1]))
                elif direction == "V":
                    neighbor_list.append((position[0], position[1]+1))
                    neighbor_list.append((position[0], position[1]-1))
                else:
                    assert(False)

                attach = [(neighbor in surgery_path.block_list) for neighbor in neighbor_list]
                is_attached = any(attach)
                if not is_attached:
                    raise LogicalQubitNotConnectedError("Surgery path does not connect target logical qubits")

        # bundle surgery paths into each timing
        time_pack = defaultdict(list)
        for surgery_path in self.surgery_path_list:
            time_pack[surgery_path.timing].append(surgery_path)

        # surgery path in same timing must not overlap
        for pack in time_pack.values():
            used_block_set = set()
            for surgery_path in pack:
                allocate_block_set = set(surgery_path.block_list)
                intersection = used_block_set & allocate_block_set
                if (len(intersection) != 0):
                    raise SurgeryPathInvalidAllocationError("Surgery paths at the same timing use common blocks")
                used_block_set = used_block_set | allocate_block_set

        # logical qubit must not be connected by both directions from the same timing
        for pack in time_pack.values():
            inst_index_list = [surgery_path.index for surgery_path in pack]
            used_logical_qubit = {}
            for inst_index in inst_index_list:
                inst = self.instance.instruction_list[inst_index]
                for target, direction in zip(inst.target_list, inst.direction_list):
                    if target in used_logical_qubit:
                        if used_logical_qubit[target] != direction:
                            raise LogicalQubitDoubleConnectError("Logical qubit is connected from different direction at the same timing")
                    else:
                        used_logical_qubit[target] = direction

    def to_string(self) -> str:
        """Visualize solution

        Returns:
            str: string formatted solution
        """
        field_org = [["."] * self.instance.chip_size[0] for _ in range(self.instance.chip_size[1])]
        for index, pos in enumerate(self.qubit_position_list):
            field_org[pos[1]-1][pos[0]-1] = str(index+1)

        s = ""
        time_pack = defaultdict(list)
        for surgery_path in self.surgery_path_list:
            time_pack[surgery_path.timing].append(surgery_path)
        for timing in sorted(time_pack.keys()):
            s += f"===== T={timing} =====\n"
            pack = time_pack[timing]
            field = deepcopy(field_org)
            for surgery_path in pack:
                for block in surgery_path.block_list:
                    field[block[1]-1][block[0]-1] = "*"

            padding_size = int(np.log10(len(self.qubit_position_list)+0.1))
            for line in field:
                line_list = [elem.center(padding_size, ' ') for elem in line]
                s += " ".join(line_list) + "\n"

        return s
