from optimize_surgery import ProblemSolution
from .sample import sample_input1, sample_output1, sample_score1, sample_input2, sample_output2, sample_score2, sample_input3, sample_output3, sample_score3


def test_sample1():
    solution = ProblemSolution(sample_input1, sample_output1)
    solution.validate()
    assert(solution.get_score() == sample_score1)
    print(solution.to_string())


def test_sample2():
    solution = ProblemSolution(sample_input2, sample_output2)
    solution.validate()
    assert(solution.get_score() == sample_score2)
    print(solution.to_string())


def test_sample3():
    solution = ProblemSolution(sample_input3, sample_output3)
    solution.validate()
    assert(solution.get_score() == sample_score3)
    print(solution.to_string())
