"""
Authors: Anne-Soline Guilbert--Ly, Romane Dauge, Pierre Gibertini

Helltaker plan computing using Answer Set Programming (ASP)
"""

import sys
from utils_helltaker import grid_from_file, check_plan
from utils_asp import grid_to_model, call_solver, convert_model


def plan_asp(infos):
    """
    :param infos: dict containing all map data
    :return: string sequence of instructions (hbgd)
    """
    asp_problem = grid_to_model(data=infos)
    models = call_solver(asp_problem=asp_problem, n_models=1)

    return convert_model(models[0])


def main():
    """
    Main function of ASP solving
    :return: print sequence of instructions to solve the given problem
    """
    # recovery the file name from the command line
    filename = sys.argv[1]

    # recovery of the grid and all the information
    infos = grid_from_file(filename)

    # plan computing
    plan = plan_asp(infos)

    # result printing
    if check_plan(plan):
        print("[OK]", plan)
    else:
        print("[Err]", plan, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
