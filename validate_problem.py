
from optimize_surgery import ProblemSolution
import sys
import argparse

parser = argparse.ArgumentParser("Validate outputs")
parser.add_argument("input_file", type=str, help="input filename")
parser.add_argument("output_file", type=str, help="output filename")
parser.add_argument("--qubit_allocate", action="store_true", help="flag for providing qubit allocation")

args = parser.parse_args()
input_str = open(args.input_file).read()
output_str = open(args.output_file).read()
flag_qubit_allocate = args.qubit_allocate
solution = ProblemSolution(input_str, output_str, flag_qubit_allocate=flag_qubit_allocate)
solution.validate()
print(f"Score: {solution.get_score()}")
print(solution.to_string())
