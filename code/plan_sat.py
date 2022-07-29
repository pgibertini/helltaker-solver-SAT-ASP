"""
Authors: Anne-Soline Guilbert--Ly, Romane Dauge, Pierre Gibertini

Helltaker plan computing using Answer Set Programming (ASP)
"""

import sys
from utils_helltaker import grid_from_file, check_plan
from utils_sat import sat_solving, convert_model


def plan_sat(infos):
    """
    :param infos: dict containing all map data
    :return: string sequence of instructions (hbgd)
    """
    sat_model = sat_solving(infos, solver='pysat')

    return convert_model(sat_model)


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
    plan = plan_sat(infos)

    # result printing
    if check_plan(plan):
        print("[OK]", plan)
    else:
        print("[Err]", plan, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
