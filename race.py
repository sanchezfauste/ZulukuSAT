#!/usr/bin/python
#######################################################################
# Copyright 2013 Josep Argelich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################

# Libraries

import sys
import os
import glob
import re

out_file = "out.txt" # Solver output
timeout = 20 # Timeout for each run
inc_to = 2 # Multiplier for timeout
inc_bug = 10000 # Multiplier for bug

# Parse CPU time in file
def get_time(out_file):
	time = None
	r = re.compile(r"^user (\d+\.\d+)")
	for l in open(out_file, "r"):
		s = re.search(r, l)
		if s:
			time = s.group(1)
			break
	return time

# Parse SATISFIABLE in file
def get_sat(out_file):
	r = re.compile(r"^s SATISFIABLE")
	for l in open(out_file, "r"):
		s = re.search(r, l)
		if s:
			return True
	return False

# Parse solver solution in file
def get_solution(out_file):
	r = re.compile(r"^v (.+)")
	for l in open(out_file, "r"):
		s = re.search(r, l)
		if s:
			sol = s.group(1).split()
			sol.insert(0, "0") # Adds a 0 at the begginig to make variable 'i' at potition 'i'
			return map(int, sol)
			break
	return None

# Check if the solution is a real solution to the benchmark file
def check_solution(solution, benchmark_file):
	instance = open(benchmark_file, "r")
	for l in instance:
		if l[0] in ["c", "p"]: # Pass comments and program line
			continue
		sl = map(int, l.split())
		sl.pop() # Remove last 0
		length = len(sl)
		for lit in sl:
			if lit == solution[abs(lit)]: # Satisfies clause
				break
			else:
				length -= 1
		if length == 0: # Falsified clause
			return False
	return True

# Check the correctness of the solution
def check_correctness(benchmark_file, out_file):
	sat = get_sat(out_file)
	if sat:
		solution = get_solution(out_file)
		if solution != None:
			return check_solution(solution, benchmark_file)
	return None

if __name__ == '__main__' :

	if len(sys.argv) != 3:
		sys.exit("Use: %s <benchmark_folder> <solver>")

	benchmark_folder = sys.argv[1]
	solver = sys.argv[2]

	# Check benchmark folder and solver
	if os.path.isdir(benchmark_folder):
		benchmark_folder = os.path.abspath(benchmark_folder)
	else:
		sys.exit("ERROR: Benchmark folder not found (%s)." % benchmark_folder)

	if os.path.isfile(solver):
		solver = os.path.abspath(solver)
	else:
		sys.exit("ERROR: Solver not found (%s)." % solver)

	# Get all the instances
	benchmark_files = glob.glob("%s/*.cnf" % benchmark_folder)
	benchmark_files.sort()
	total_time = 0
	# Run the solver for al the instances
	for bf in benchmark_files:
		sys.stdout.write("File %s... " % os.path.basename(bf))
		sys.stdout.flush()
		# Run the solver under limits.sh and computing time
		os.system("(time -p ./limits.sh %s %s) > %s 2>&1" % (solver, bf, out_file))
		#Check result
		correct = check_correctness(bf, out_file)
		if correct == True: # The solution is correct
			#Get Time
			time = get_time(out_file)
			if time == None: # This should not happend
				time = timeout * inc_to
				sys.stdout.write("Time not found! time = %.2f\n" % time)
			else:
				time = float(time)
				sys.stdout.write("OK! time = %.2f\n" % time)
		elif correct == None: # There is no solution
			time = timeout * inc_to
			sys.stdout.write("No solution found! time = %i\n" % time)
		elif correct == False: # There is a bug in the solution
			time = timeout * inc_bug
			sys.stdout.write("Wrong solution! time = %i\n" % time)
		total_time += time
		sys.stdout.write("Current time = %.2f\n" % total_time)
	os.system("rm %s" % out_file)

	# Results
	sys.stdout.write("Total time = %.2f\n" % total_time)