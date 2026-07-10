
class SolutionBuilder:
    def __init__(self, flag_qubit_allocate: bool = False) -> None:
        self.timing_list: list[int] = []
        self.path_list: list[list[tuple[int, int]]] = []
        self.qubit_position_list: list[tuple[int,int]] = []
        self.flag_qubit_allocate = flag_qubit_allocate

    def add_surgery_path(self, timing: int, pairs: list[tuple[int, int]]) -> None:
        self.timing_list.append(timing)
        self.path_list.append(pairs)

    def add_qubit_allocation(self, position: tuple[int, int]) -> None:
        if not self.flag_qubit_allocate:
            raise ValueError("flag_qubit_allocation is disbaled, but qubit allocations are set")
        self.qubit_position_list.append(position)

    def dump_str(self) -> None:
        s = ""
        if self.flag_qubit_allocate:
            for position in self.qubit_position_list:
                s += f"{position[0]} {position[1]}\n"

        for timing, path in zip(self.timing_list, self.path_list):
            path_str = [f"{x} {y}" for (x, y) in path]
            s += f"{timing} {len(path)} " + " ".join(path_str) + "\n"
        return s
