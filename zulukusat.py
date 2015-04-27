#!/usr/bin/python

#######################################################################
# Copyright 2015 Marc Sanchez Fauste

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

import sys
import random

class SatProblem:

    def __init__(self, cnf_file):
        self.clauses = {}
        self.clauses_set = set()
        self.number_of_vars = 0
        if cnf_file:
            self.read(cnf_file)

    def read(self, cnf_file):
        f = open(cnf_file, "r")
        for line in f:
            l = line.split()
            if len(l) != 0 and l[0] != 'c':
                if l[0] == 'p':
                    self.number_of_vars = int(l[2])
                else:
                    clause = []
                    for elem in sorted([int(lit) for lit in l[:-1]], key=abs):
                        literal = None
                        if elem > 0:
                            literal = (elem, True)
                        else:
                            literal = (abs(elem), False)
                        clause.append(literal)
                    self.clauses_set.add(tuple(clause))
        f.close()
        for clause in self.clauses_set:
            for literal in clause:
                if literal[0] not in self.clauses:
                    self.clauses[literal[0]] = set()
                self.clauses[literal[0]].add(tuple(clause))

class Interpretation:

    def __init__(self, sat_problem):
        self.sat_problem = sat_problem
        self.values = ["UNUSED"]
        self.unsatisfied_clauses = set()
        for i in xrange(sat_problem.number_of_vars):
                self.values.append(True)

    def set_random_interpretation(self):
        for i in xrange(1, sat_problem.number_of_vars):
            if random.random() < 0.5:
                self.values[i] = True
            else:
                self.values[i] = False
        self.update_unsatisfied_clauses_set()

    def flip_variable(self, variable, update_unsatisfied_clauses=True):
        self.values[variable] = not self.values[variable]
        if update_unsatisfied_clauses:
            self.update_unsatisfied_clauses_set(variable)

    def show(self):
        sys.stdout.write("v")
        for i in xrange(1, len(self.values)):
            if self.values[i]:
                sys.stdout.write(" %i" % i)
            else:
                sys.stdout.write(" %i" % -i)
        sys.stdout.write(" 0\n")

    def satisfies_problem(self):
        return len(self.unsatisfied_clauses) == 0

    def clause_is_satisfied(self, clause):
        for literal in clause:
            if self.values[literal[0]] == literal[1]:
                return True
        return False

    def get_unsatisfied_clause(self):
        return random.sample(self.unsatisfied_clauses, 1)[0]

    def get_number_of_broken_clauses(self, clauses):
        broken_clausules = 0
        for clause in clauses:
            if not self.clause_is_satisfied(clause):
                broken_clausules += 1
        return broken_clausules

    def update_unsatisfied_clauses_set(self, changed_variable=None):
        if changed_variable:
            if changed_variable in self.sat_problem.clauses:
                for clause in self.sat_problem.clauses[changed_variable]:
                    if self.clause_is_satisfied(clause):
                        if clause in self.unsatisfied_clauses:
                            self.unsatisfied_clauses.remove(clause)
                    else:
                        if clause not in self.unsatisfied_clauses:
                            self.unsatisfied_clauses.add(clause)
        else:
            self.unsatisfied_clauses.clear()
            for clause in self.sat_problem.clauses_set:
                if not self.clause_is_satisfied(clause):
                    self.unsatisfied_clauses.add(clause)

    def get_best_variable_to_flip(self):
        best_literal_to_flip = None
        b = len(sat_problem.clauses_set) + 1
        for literal in self.get_unsatisfied_clause():
            clauses_to_evaluate = self.sat_problem.clauses[literal[0]]
            broken_clauses = self.get_number_of_broken_clauses(clauses_to_evaluate)
            self.flip_variable(literal[0], False)
            broken_clauses_flipped = self.get_number_of_broken_clauses(clauses_to_evaluate)
            self.flip_variable(literal[0], False)
            broken = broken_clauses_flipped - broken_clauses
            if b > broken:
                b = broken
                best_literal_to_flip = literal
        return b, best_literal_to_flip

class Walksat:

    @staticmethod
    def solve_problem(sat_problem, max_tries=1000, max_flips=1000, p=0.5):
        interpretation = Interpretation(sat_problem)
        for t in xrange(max_tries):
            interpretation.set_random_interpretation()
            for flip in xrange(max_flips):
                if interpretation.satisfies_problem():
                    return interpretation
                b, best_literal_to_flip = interpretation.get_best_variable_to_flip()
                if b > 0 and random.random() < p:
                    interpretation.flip_variable(random.randint(1, sat_problem.number_of_vars))
                else:
                    interpretation.flip_variable(best_literal_to_flip[0])
        return None

if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print "Use:", sys.argv[0], "<sat_problem.cnf>"
        sys.exit(1)
    sat_problem = SatProblem(sys.argv[1])
    interpretation = Walksat.solve_problem(sat_problem, max_flips=sat_problem.number_of_vars, max_tries=4000000)
    print "c ZulukuSAT Solver"
    if interpretation:
        print "s SATISFIABLE"
        interpretation.show()
    else:
        print "s NO SOLUTION FOUND"
