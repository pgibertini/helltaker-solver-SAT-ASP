"""
Authors: Anne-Soline Guilbert--Ly, Romane Dauge, Pierre Gibertini

This module contains the necessary functions to solve the problem in ASP
"""
import sys
from time import time
from typing import List
import clingo
from utils_helltaker import grid_from_file, convert_action


def grid_to_model(data) -> str:
    """
    :param data: dict containing all the map data
    :return: ASP description of the problem
    """
    const = f"#const horizon={data.get('max_steps')}.\n"
    cells = ""
    hero = ""
    demonesses = ""
    key = ""
    lock = ""
    spikes = ""
    traps = ""
    blocks = ""
    mobs = ""

    grid = data.get("grid")

    for i in range(data.get("m")):
        for j in range(data.get("n")):
            if grid[i][j] != "#":
                cells += f"cell({i}, {j}).\n"

            if grid[i][j] == "H":
                hero = f"fluent(at({i}, {j}), 0).\n"
            elif grid[i][j] == "D":
                demonesses += f"demoness({i}, {j}).\n"
            elif grid[i][j] == "K":
                key += f"key({i}, {j}).\n"
            elif grid[i][j] == "L":
                lock += f"fluent(lock({i}, {j}), 0).\n"
            elif grid[i][j] == "S":
                spikes += f"fluent(spike({i}, {j}), 0).\n"
            elif grid[i][j] == "T":
                traps += f"fluent(trap({i}, {j}), 0, safe).\n"
            elif grid[i][j] == "U":
                traps += f"fluent(trap({i}, {j}), 0, unsafe).\n"
            elif grid[i][j] == "B":
                blocks += f"fluent(block({i}, {j}), 0).\n"
            elif grid[i][j] == "M":
                mobs += f"fluent(mob({i}, {j}), 0).\n"
            elif grid[i][j] == "O":
                blocks += f"fluent(block({i}, {j}), 0).\n"
                spikes += f"fluent(spike({i}, {j}), 0).\n"
            elif grid[i][j] == "P":
                blocks += f"fluent(block({i}, {j}), 0).\n"
                traps += f"fluent(trap({i}, {j}), 0, safe).\n"
            elif grid[i][j] == "Q":
                blocks += f"fluent(block({i}, {j}), 0).\n"
                traps += f"fluent(trap({i}, {j}), 0, unsafe).\n"

    return (
        "\n%%% MAP DESCRIPTION\n"
        + const
        + cells
        + demonesses
        + key
        + lock
        + spikes
        + traps
        + blocks
        + mobs
        + hero
        + RULES
    )


def convert_model(model: List[clingo.Symbol]) -> str:
    """
    :param model: an ordered list of symbol "do(action, time)"
    :return: corresponding instructions (hbgd)
    """
    plan = ""
    for atom in model:
        plan += convert_action(atom.arguments[0].name)

    return plan


def call_solver(asp_problem: str, n_models: int = 0) -> List[List[clingo.Symbol]]:
    """
    :param asp_problem: a string containing the problem written in ASP
    :param n_models: the number of desired models (0 for all)
    :return: a list of models
    """
    ctl = clingo.Control([f"-n {n_models}"])
    ctl.add("base", [], asp_problem)
    ctl.ground([("base", [])])

    models = []

    with ctl.solve(yield_=True) as handle:
        for model in handle:
            actions = []
            for atom in model.symbols(atoms=True):
                if atom.match("do", 2):
                    actions.append(atom)

            actions.sort(key=lambda a: a.arguments[1].number)
            models.append(actions)

    return models


RULES = """
step(0..horizon-1).

%%% GENERATION OF ACTIONS
% list of possible actions
action(up; down; left; right; hurt).
action(push_block_up; push_block_down; push_block_left; push_block_right).
action(push_mob_up; push_mob_down; push_mob_left; push_mob_right).
action(nop).
% generation
{do(A, T): action(A)}=1 :- step(T).


%%% OBJECTIVE
% test
achieved(T) :- meet(demoness(_, _), T), demoness(_, _).
:- not achieved(_).
% conditions
meet(demoness(X+1, Y), T) :- fluent(at(X, Y), T), demoness(X+1, Y).
meet(demoness(X-1, Y), T) :- fluent(at(X, Y), T), demoness(X-1, Y).
meet(demoness(X, Y+1), T) :- fluent(at(X, Y), T), demoness(X, Y+1).
meet(demoness(X, Y-1), T) :- fluent(at(X, Y), T), demoness(X, Y-1).


%%% ACTION: nop
:- achieved(T), do(A, T), A != nop. % only possible action when finished: nop
:- do(nop, T), not achieved(T). % but 'nop' can only be done after finishing

%%% ACTION: up
% precondition
:- do(up, T), fluent(at(X, Y), T), not cell(X-1, Y).
:- do(up, T), fluent(at(X, Y), T), fluent(block(X-1, Y), T).
:- do(up, T), fluent(at(X, Y), T), fluent(mob(X-1, Y), T).
% effect
fluent(at(X-1, Y), T+1) :- do(up, T), fluent(at(X, Y), T).
removed(at(X, Y), T) :- do(up, T), fluent(at(X, Y), T).

%%% ACTION: down
% precondition
:- do(down, T), fluent(at(X, Y), T), not cell(X+1, Y).
:- do(down, T), fluent(at(X, Y), T), fluent(block(X+1, Y), T).
:- do(down, T), fluent(at(X, Y), T), fluent(mob(X+1, Y), T).
% effect
fluent(at(X+1, Y), T+1) :- do(down, T), fluent(at(X, Y), T).
removed(at(X, Y), T) :- do(down, T), fluent(at(X, Y), T).

%%% ACTION: left
% precondition
:- do(left, T), fluent(at(X, Y), T), not cell(X, Y-1).
:- do(left, T), fluent(at(X, Y), T), fluent(block(X, Y-1), T).
:- do(left, T), fluent(at(X, Y), T), fluent(mob(X, Y-1), T).
% effect
fluent(at(X, Y-1), T+1) :- do(left, T), fluent(at(X, Y), T).
removed(at(X, Y), T) :- do(left, T), fluent(at(X, Y), T).

%%% ACTION: right
% precondition
:- do(right, T), fluent(at(X, Y), T), not cell(X, Y+1).
:- do(right, T), fluent(at(X, Y), T), fluent(block(X, Y+1), T).
:- do(right, T), fluent(at(X, Y), T), fluent(mob(X, Y+1), T).
% effect
fluent(at(X, Y+1), T+1) :- do(right, T), fluent(at(X, Y), T).
removed(at(X, Y), T) :- do(right, T), fluent(at(X, Y), T).

%%% ACTION: push_block_up
% precondition
:- do(push_block_up, T), fluent(at(X, Y), T), not fluent(block(X-1, Y), T).
% effects
removed(block(X-1, Y), T) :-
    do(push_block_up, T),
    fluent(at(X, Y), T),
    cell(X-2, Y),
    not fluent(block(X-2, Y), T),
    not fluent(mob(X-2, Y), T),
    not fluent(lock(X-2, Y), T),
    not demoness(X-2, Y).
fluent(block(X-2, Y), T+1) :- do(push_block_up, T), fluent(at(X, Y), T), removed(block(X-1, Y), T).

%%% ACTION: push_block_down
% precondition
:- do(push_block_down, T), fluent(at(X, Y), T), not fluent(block(X+1, Y), T).
% effectS
removed(block(X+1, Y), T) :-
    do(push_block_down, T),
    fluent(at(X, Y), T),
    cell(X+2, Y),
    not fluent(block(X+2, Y), T),
    not fluent(mob(X+2, Y), T),
    not fluent(lock(X+2, Y), T),
    not demoness(X+2, Y).
fluent(block(X+2, Y), T+1) :- do(push_block_down, T), fluent(at(X, Y), T), removed(block(X+1, Y), T).

%%% ACTION: push_block_left
% precondition
:- do(push_block_left, T), fluent(at(X, Y), T), not fluent(block(X, Y-1), T).
% effects
removed(block(X, Y-1), T) :-
    do(push_block_left, T),
    fluent(at(X, Y), T),
    cell(X, Y-2),
    not fluent(block(X, Y-2), T),
    not fluent(mob(X, Y-2), T),
    not fluent(lock(X, Y-2), T),
    not demoness(X, Y-2).
fluent(block(X, Y-2), T+1) :- do(push_block_left, T), fluent(at(X, Y), T), removed(block(X, Y-1), T).

%%% ACTION: push_block_right
% precondition
:- do(push_block_right, T), fluent(at(X, Y), T), not fluent(block(X, Y+1), T).
% effects
removed(block(X, Y+1), T) :-
    do(push_block_right, T),
    fluent(at(X, Y), T),
    cell(X, Y+2),
    not fluent(block(X, Y+2), T),
    not fluent(mob(X, Y+2), T),
    not fluent(lock(X, Y+2), T),
    not demoness(X, Y+2).
fluent(block(X, Y+2), T+1) :- do(push_block_right, T), fluent(at(X, Y), T), removed(block(X, Y+1), T).

%%% ACTION: push_mob_up
% precondition
:- do(push_mob_up, T), fluent(at(X, Y), T), not fluent(mob(X-1, Y), T).
% effect
removed(mob(X-1, Y), T) :- do(push_mob_up, T), fluent(at(X, Y), T).
fluent(mob(X-2, Y), T) :- do(push_mob_up, T), fluent(at(X, Y), T).

%%% ACTION: push_mob_down
% precondition
:- do(push_mob_down, T), fluent(at(X, Y), T), not fluent(mob(X+1, Y), T).
% effect
removed(mob(X+1, Y), T) :- do(push_mob_down, T), fluent(at(X, Y), T).
fluent(mob(X+2, Y), T) :- do(push_mob_down, T), fluent(at(X, Y), T).

%%% ACTION: push_mob_left
% precondition
:- do(push_mob_left, T), fluent(at(X, Y), T), not fluent(mob(X, Y-1), T).
% effects
removed(mob(X, Y-1), T) :- do(push_mob_left, T), fluent(at(X, Y), T).
fluent(mob(X, Y-2), T) :- do(push_mob_left, T), fluent(at(X, Y), T).

%%% ACTION: push_mob_right
% precondition
:- do(push_mob_right, T), fluent(at(X, Y), T), not fluent(mob(X, Y+1), T).
% effects
removed(mob(X, Y+1), T) :- do(push_mob_right, T), fluent(at(X, Y), T).
fluent(mob(X, Y+2), T) :- do(push_mob_right, T), fluent(at(X, Y), T).

%%% DEATH OF MOBS
removed(mob(X, Y), T) :- fluent(mob(X, Y), T), fluent(spike(X, Y), T+1).
removed(mob(X, Y), T) :- fluent(mob(X, Y), T), fluent(block(X, Y), T).
removed(mob(X, Y), T) :- fluent(mob(X, Y), T), not cell(X, Y).

%%% LOCK AND KEY
% condition of lock
:- fluent(at(X, Y), T), fluent(lock(X, Y), T), not fluent(have(key), T).
% effect of key
fluent(have(key), T) :- fluent(at(X, Y), T), key(X, Y).
removed(lock(X, Y), T) :- fluent(at(X, Y), T), fluent(lock(X, Y), T).

%%% ACTION: hurt
% generation
fluent(spike(X, Y), T) :- fluent(trap(X, Y), T, unsafe). % unsafe trap is equivalent to spike
removed(spike(X, Y), T) :- fluent(trap(X, Y), T, unsafe). % prevent non-desired apparition of spike
fluent(trap(X, Y), T+1, safe) :- fluent(trap(X, Y), T, unsafe), do(A, T), A != hurt. % safe trap become unsafe if action different from hurt
fluent(trap(X, Y), T+1, unsafe) :- fluent(trap(X, Y), T, safe), do(A, T), A != hurt. % unsafe trap become safe if action different from hurt
fluent(trap(X, Y), T+1, unsafe) :- fluent(trap(X, Y), T, unsafe), do(A, T), A = hurt. % unsafe trap stay unsafe if hurt
fluent(trap(X, Y), T+1, safe) :- fluent(trap(X, Y), T, safe), do(A, T), A = hurt. % safe trap stay safe if hurt
% precondition
:- fluent(at(X, Y), T), fluent(spike(X, Y), T), not do(hurt, T-1), not do(hurt, T). % forced to hurt if on spike and not hurt the turn before
:- do(hurt, T-1), do(hurt, T). % can't hurt two turn in a row
:- do(hurt, T), fluent(at(X, Y), T), not fluent(spike(X, Y), T). % can't hurt if not on spike

%%% FRAME PROBLEM
fluent(F, T+1) :- fluent(F, T), T+1 < horizon, not removed(F, T).

#show do/2.
"""


def test():
    """
    Test function of ASP solving
    Run: python3 utils_asp.py ./levels/level1.txt
    """
    start = time()
    filename = sys.argv[1]
    infos = grid_from_file(filename)

    asp_problem = grid_to_model(data=infos)

    print("SOLVER INPUT:\n")
    print(asp_problem)

    print("MODELS")
    for i_model, model in enumerate(call_solver(asp_problem, 0)):
        print(f"\nModel #{i_model+1}:")
        for atom in model:
            print(atom)
        print("Instructions:", convert_model(model))

    print(f"\nRunning time: {time() - start}s")


if __name__ == "__main__":
    test()
