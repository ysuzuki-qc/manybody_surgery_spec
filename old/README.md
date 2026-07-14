# Lattice surgery optimization

## Problem Statement

See `optimize_surgery.md` and `optimize_surgery.html`.

## Generating Problems

Running `python generate_problem.py` creates a `pset` folder and generates problems as `*.in` files. Example outputs for `sample1`, `sample2`, and `sample3` are also generated as `*.out` files.

## Testing Problems

You can validate a solution by running `python validate_problem.py <input_file> <output_file>`.
To specify qubit positions, add `--allocate_qubit` to the arguments.

```
python .\validate_problem.py ./pset/sample1.in ./pset/sample1.out
python .\validate_problem.py ./pset/sample1.in ./pset/sample1_with_allocate.out --qubit_allocate
```

## Tests and Validation

Run `pytest` to execute the validation tests.

## Examples

For other use cases, see `demo_sample.py` and `demo_validation.py`.
