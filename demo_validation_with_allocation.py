
from optimize_surgery import ProblemSolution, ProblemInstance

with open("./pset/sample1.in") as fin:
    input_str = fin.read()

print(input_str)

output_str = '''\
1 1
2 1
1 2 1 2 2 2
2 0
'''

solution = ProblemSolution(input_str, output_str, flag_qubit_allocate=True)
solution.validate()
print(solution.to_string())


