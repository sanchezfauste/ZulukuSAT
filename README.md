# ZulukuSAT Solver
An implementation of Walksat algorithm in Python 2.7.x

# Considerations

- This solver is an implementation of Walksat algorithm, considering there may be some repeated clauses and also may have some variables that not appear in any clause.

- Only instances generated with a cnf random generator included in this project (rnd-cnf-gen.py) are tested. The directory benchmarks contains some random instances created with this generator. This solver is optimized to run this random generated instances.

- The file race.py runs a race testing some benchmarks with a timeout of 20 seconds for every benchmark.

- The main algorithm of solver is implemented in zulukusat.py file.

- If you want to run a race you have to give x permissions to files: `race.py, limits.sh and zulukusat.py` 

# Basic usage

You can run ZulukuSAT Solver with `$ python zulukusat.py <cnf_benchmark>`

You can run a race with `$ python race.py benchmarks_folder zulukusat.py`
