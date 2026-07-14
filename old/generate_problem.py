from optimize_surgery.problem_set import generate_problem_set
import os


if __name__ == "__main__":
    folder_name = "pset"
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    os.chdir(folder_name)
    generate_problem_set()
