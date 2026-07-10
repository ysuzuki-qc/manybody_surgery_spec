
from optimize_surgery import ProblemSolution, ProblemInstance

with open("./pset/sample1.in") as fin:
    input_str = fin.read()

print(input_str)

output_str = '''\
1 3 2 1 3 1 4 1
2 1 3 2
'''

solution = ProblemSolution(input_str, output_str)
solution.validate()
print(solution.to_string())


