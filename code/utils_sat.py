"""
Authors: Anne-Soline Guilbert--Ly, Romane Dauge, Pierre Gibertini

This module contains the necessary functions to solve the problem in ASP
"""

import sys
from time import time
from typing import List, Tuple, Set
from itertools import combinations
import subprocess
from utils_helltaker import grid_from_file, convert_action


# alias de type
Grid = List[List[str]]
Variable = int
Literal = int
Clause = List[Literal]
Map = List[List[Literal]]
Coord = Tuple[int, int]


ACTIONS = (
    "left",
    "right",
    "up",
    "down",
    "hurt",
    "push_block_left",
    "push_block_right",
    "push_block_up",
    "push_block_down",
    "push_mob_left",
    "push_mob_right",
    "push_mob_up",
    "push_mob_down",
)


def grid_to_coords_dict(grid: Grid) -> dict:
    """
    :param grid: grid of the level
    :return: dict containing position of each element
    """
    coords = {
        "cells": [],
        "empty": [],
        "hero": [],
        "demonesses": [],
        "key": [],
        "lock": [],
        "spikes": [],
        "traps_safe": [],
        "traps_unsafe": [],
        "blocks": [],
        "mobs": [],
    }

    for i, line in enumerate(grid):
        for j, cell in enumerate(line):
            if cell != "#":
                coords["cells"].append((i, j))
            if cell in ["S", " ", "T", "U", "K"]:
                coords["empty"].append((i, j))
            if cell == "H":
                coords["hero"].append((i, j))
            elif cell == "D":
                coords["demonesses"].append((i, j))
            elif cell == "K":
                coords["key"].append((i, j))
            elif cell == "L":
                coords["lock"].append((i, j))
            elif cell == "S":
                coords["spikes"].append((i, j))
            elif cell == "T":
                coords["traps_safe"].append((i, j))
            elif cell == "U":
                coords["traps_unsafe"].append((i, j))
            elif cell == "B":
                coords["blocks"].append((i, j))
            elif cell == "M":
                coords["mobs"].append((i, j))
            elif cell == "O":
                coords["blocks"].append((i, j))
                coords["spikes"].append((i, j))
            elif cell == "P":
                coords["blocks"].append((i, j))
                coords["traps_safe"].append((i, j))
            elif cell == "Q":
                coords["blocks"].append((i, j))
                coords["traps_unsafe"].append((i, j))

    return coords


def vocabulary(coords: dict, t_max: int) -> dict:
    """
    :param coords: dict containing coord of each element of the map
    :param t_max: horizon
    :return: dict containing all the vocabulary
    """
    cells = coords["cells"]
    traps = coords["traps_unsafe"] + coords["traps_safe"]

    act_vars = [("do", t, a) for t in range(t_max) for a in ACTIONS]
    at_vars = [("at", t, c) for t in range(t_max + 1) for c in cells]
    spike_vars = [("spike", t, c) for t in range(t_max + 1) for c in cells]
    traps_vars = [("trap", t, c) for t in range(t_max + 1) for c in traps]
    have_key_vars = [("have_key", t) for t in range(t_max + 1)]
    empty_cell_vars = [("empty", t, c) for t in range(t_max + 1) for c in cells]
    block_vars = [("block", t, c) for t in range(t_max + 1) for c in cells]
    mob_vars = [("mob", t, c) for t in range(t_max + 1) for c in cells]

    return {
        v: i + 1
        for i, v in enumerate(
            act_vars
            + at_vars
            + spike_vars
            + traps_vars
            + have_key_vars
            + block_vars
            + empty_cell_vars
            + mob_vars
        )
    }


def clauses_exactly_one_action(var2n: dict, t_max: int) -> List[Clause]:
    """
    :param var2n: dict giving the corresponding number for each variable
    :param t_max: horizon
    :return: clauses to have exactly one action each turn
    """
    at_least_one_act = [[var2n[("do", t, a)] for a in ACTIONS] for t in range(t_max)]
    at_most_one_act = [
        [-var2n[("do", t, a1)], -var2n[("do", t, a2)]]
        for t in range(t_max)
        for a1, a2 in combinations(ACTIONS, 2)
    ]
    return at_least_one_act + at_most_one_act


def clauses_initial_state(var2n: dict, coords: dict, t_max: int) -> List[Clause]:
    """
    :param var2n: dict giving the corresponding number for each variable
    :param coords: dict containing coord of each element of the map
    :param t_max: horizon
    :return: clauses corresponding to the initial state
    """
    clauses = []
    # HERO
    for coord in coords["hero"]:
        clauses.append([var2n[("at", 0, coord)]])
    for coord in [cell for cell in coords["cells"] if cell not in coords["hero"]]:
        clauses.append([-var2n[("at", 0, coord)]])

    # SPIKES AND TRAPS
    # les spikes sont toujours là, et une case qui n'est pas un spike ou un trap
    # ne sera jamais un spike
    for t in range(t_max + 1):
        for coord in coords["spikes"]:
            clauses.append([var2n[("spike", t, coord)]])
        for coord in [
            cell
            for cell in coords["cells"]
            if cell
            not in coords["spikes"] + coords["traps_safe"] + coords["traps_unsafe"]
        ]:
            clauses.append([-var2n[("spike", t, coord)]])

    # traps safe
    for coord in coords["traps_safe"]:
        clauses.append([var2n[("trap", 0, coord)]])

    # traps unsafe
    for coord in coords["traps_unsafe"]:
        clauses.append([-var2n[("trap", 0, coord)]])

    # LOCK AND KEY
    # on ne commence pas avec la clé
    clauses.append([-var2n[("have_key", 0)]])

    # BLOCKS
    for coord in coords["blocks"]:
        clauses.append([var2n[("block", 0, coord)]])
    for coord in [cell for cell in coords["cells"] if cell not in coords["blocks"]]:
        clauses.append([-var2n[("block", 0, coord)]])

    # EMPTY CELLS (without block, lock, mob or demoness)
    for coord in coords["empty"]:
        clauses.append([var2n[("empty", 0, coord)]])
    for coord in [cell for cell in coords["cells"] if cell not in coords["empty"]]:
        clauses.append([-var2n[("empty", 0, coord)]])

    # les cases avec demoness ne seront jamais vides
    # (et avec lock non plus dans un but de simplicité)
    for t in range(1, t_max):
        for coord in coords["demonesses"] + coords["lock"]:
            clauses.append([-var2n[("empty", t, coord)]])

    # MOBS
    for coord in coords["mobs"]:
        clauses.append([var2n[("mob", 0, coord)]])
    for coord in [cell for cell in coords["cells"] if cell not in coords["mobs"]]:
        clauses.append([-var2n[("mob", 0, coord)]])

    return clauses


def succ(at: Coord, action: str) -> dict:
    """
    :param at: position of where is done the action
    :param action: string correspond to the action
    :return: dict containing the pos of the successor for the given action
    """
    i, j = at
    return {
        "left": (i, j - 1),
        "right": (i, j + 1),
        "up": (i - 1, j),
        "down": (i + 1, j),
        "hurt": (i, j),
        "push_block_left": (i, j),
        "push_block_right": (i, j),
        "push_block_up": (i, j),
        "push_block_down": (i, j),
        "push_mob_left": (i, j),
        "push_mob_right": (i, j),
        "push_mob_up": (i, j),
        "push_mob_down": (i, j),
    }[action]


def where_pushed(at: Coord, action: str) -> dict:
    """
    :param at: position of where is done the action
    :param action: action of pushing
    :return: ((pos of the pushed object), (where is pushed the object))
    """
    i, j = at
    return {
        "push_block_left": ((i, j - 1), (i, j - 2)),
        "push_block_right": ((i, j + 1), (i, j + 2)),
        "push_block_up": ((i - 1, j), (i - 2, j)),
        "push_block_down": ((i + 1, j), (i + 2, j)),
        "push_mob_left": ((i, j - 1), (i, j - 2)),
        "push_mob_right": ((i, j + 1), (i, j + 2)),
        "push_mob_up": ((i - 1, j), (i - 2, j)),
        "push_mob_down": ((i + 1, j), (i + 2, j)),
    }[action]


def adjacent(at: Coord) -> List[Coord]:
    """
    :param at: coord
    :return: list of directly adjacent cells
    """
    i, j = at
    return [
        (i, j - 1),
        (i, j + 1),
        (i - 1, j),
        (i + 1, j),
    ]


def adjacent_block(at: Coord) -> List[Coord]:
    """
    :param at: coord
    :return: list of non directly adjacent cells coords
    """
    i, j = at
    return [
        (i, j - 2),
        (i, j + 2),
        (i - 2, j),
        (i + 2, j),
    ]


def clauses_successor_from_given_position(
    var2n: dict, cells: List[Coord], t_max: int, position: Coord
) -> List[Clause]:
    """
    :param var2n: dict giving the corresponding number for each variable
    :param cells: list of all cells coords
    :param t_max: horizon
    :param position: position where the action is done
    :return: clauses corresponding to successor from given position

    """
    Successors = {a: succ(position, a) for a in ACTIONS}

    # transitions impossibles, entre deux cases non voisines ou égales
    clauses = [
        [-var2n[("at", t, position)], -var2n[("at", t + 1, c)]]
        for t in range(t_max)
        for c in cells
        if not (c in Successors.values())
    ]

    # actions interdites, qui feraient sortir du plateau (mur ou bord)
    clauses += [
        [-var2n[("at", t, position)], -var2n[("do", t, a)]]
        for t in range(t_max)
        for a, c in Successors.items()
        if not (c in cells)
    ]

    # transitions possibles
    for a, c in Successors.items():
        if c in cells:
            # at(t,position) AND do(t,a) -> at(t+1,c)
            clauses += [
                [
                    -var2n[("at", t, position)],
                    -var2n[("do", t, a)],
                    var2n[("at", t + 1, c)],
                ]
                for t in range(t_max)
            ]
            # unicité de l'état à l'issue de l'action
            clauses += [
                [
                    -var2n[("at", t, position)],
                    -var2n[("do", t, a)],
                    -var2n[("at", t + 1, c1)],
                ]
                for t in range(t_max)
                for c1 in Successors.values()
                if c1 != c and c1 in cells
            ]

    return clauses


def clauses_spikes(var2n: dict, t_max: int, position: Coord) -> List[Clause]:
    """
    :param var2n: dict giving the corresponding number for each variable
    :param t_max: horizon
    :param position: cell position
    :return: clauses corresponding to spikes
    """
    clauses = []

    # interdit de hurt si pas sur spike
    clauses += [
        [
            -var2n[("at", t, position)],
            -var2n[("do", t, "hurt")],
            var2n[("spike", t, position)],
        ]
        for t in range(t_max)
    ]

    # pas hurt deux tours de suite
    clauses += [
        [-var2n[("do", t, "hurt")], -var2n[("do", t + 1, "hurt")]]
        for t in range(t_max - 1)
    ]

    # obliger de hurt si sur spike et pas hurt au dernier tour
    clauses += [
        [
            var2n[("do", t - 1, "hurt")],
            var2n[("do", t, "hurt")],
            -var2n[("at", t, position)],
            -var2n[("spike", t, position)],
        ]
        for t in range(1, t_max)
    ]

    return clauses


def clauses_traps(var2n: dict, t_max: int, position: Coord) -> List[Clause]:
    """
    :param var2n: dict giving the corresponding number for each variable
    :param t_max: horizon
    :param position: cell position
    :return: clauses corresponding to traps
    """
    clauses = []

    # un trap unsafe est équivalent à un spike
    clauses += [
        [var2n[("trap", t, position)], var2n[("spike", t, position)]]
        for t in range(t_max)
    ]

    # un trap safe n'est pas un spike
    clauses += [
        [-var2n[("trap", t, position)], -var2n[("spike", t, position)]]
        for t in range(t_max)
    ]

    # un trap unsafe reste unsafe si l'action est hurt
    clauses += [
        [
            -var2n[("do", t, "hurt")],
            var2n[("trap", t, position)],
            -var2n[("trap", t + 1, position)],
        ]
        for t in range(t_max)
    ]

    # un trap safe reste safe si l'action est hurt
    clauses += [
        [
            -var2n[("do", t, "hurt")],
            -var2n[("trap", t, position)],
            var2n[("trap", t + 1, position)],
        ]
        for t in range(t_max)
    ]

    # un trap unsafe devient safe si l'action n'est pas hurt
    clauses += [
        [
            var2n[("do", t, "hurt")],
            var2n[("trap", t, position)],
            var2n[("trap", t + 1, position)],
        ]
        for t in range(t_max)
    ]

    # un trap safe devient unsafe si l'action n'est pas hurt
    clauses += [
        [
            var2n[("do", t, "hurt")],
            -var2n[("trap", t, position)],
            -var2n[("trap", t + 1, position)],
        ]
        for t in range(t_max)
    ]

    return clauses


def clauses_lock_and_key(
    var2n: dict, t_max: int, lock: Coord, key: Coord
) -> List[Clause]:
    """
    :param var2n: dict giving the corresponding number for each variable
    :param t_max: horizon
    :param lock: lock position
    :param key: key position
    :return: clauses corresponding to lock and key
    """
    clauses = []

    # on récupère la clé sur la case de la clé
    clauses += [[-var2n[("at", t, key)], var2n[("have_key", t)]] for t in range(t_max)]

    # si on a la clé, on continue de l'avoir
    clauses += [[-var2n[("have_key", t)], var2n[("have_key", t + 1)]] for t in range(t_max)]

    # on ne récupère pas la clé si on n'est pas sur la case et qu'on ne l'a pas déjà
    clauses += [
        [var2n[("at", t, key)], var2n[("have_key", t - 1)], -var2n[("have_key", t)]]
        for t in range(1, t_max)
    ]

    # on ne pas pas être sur la case du lock si on n'a pas la clé
    clauses += [[var2n[("have_key", t)], -var2n[("at", t, lock)]] for t in range(t_max)]

    return clauses


def clauses_empty(var2n: dict, t_max: int, cell: Coord) -> List[Clause]:
    """
    :param var2n: dict giving the corresponding number for each variable
    :param t_max: horizon
    :param cell: cell position
    :return: clauses corresponding to empty cell
    """
    clauses = []

    # une case avec mob n'est pas vide
    clauses += [[-var2n[("mob", t, cell)], -var2n[("empty", t, cell)]] for t in range(t_max)]

    # une case avec block n'est pas vide
    clauses += [
        [-var2n[("block", t, cell)], -var2n[("empty", t, cell)]] for t in range(t_max)
    ]

    return clauses


def clauses_blocks(
    var2n: dict, t_max: int, cells: List[Coord], position: Coord
) -> List[Clause]:
    """
    :param var2n: dict giving the corresponding number for each variable
    :param t_max: horizon
    :param cells: list of all cells coords
    :param position: cell position
    :return: clauses corresponding to blocks
    """
    pushing_action = (
        "push_block_left",
        "push_block_right",
        "push_block_up",
        "push_block_down",
    )
    moving_action = ("left", "right", "up", "down")

    WherePushed = {a: where_pushed(position, a) for a in pushing_action}
    Move = {a: succ(position, a) for a in moving_action}

    clauses = []

    # PRECONDITIONS OF PUSHING
    # interdit de push une cellule qui n'est pas block
    clauses += [
        [-var2n[("at", t, position)], var2n[("block", t, c[0])], -var2n[("do", t, a)]]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if c[0] in cells
    ]

    # interdit de push dans un mur
    clauses += [
        [-var2n[("at", t, position)], -var2n[("do", t, a)]]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if not (c[0] in cells)
    ]

    # EVOLUTIONS OF BLOCKS
    # les block non push restent à leur place
    clauses += [
        [
            -var2n[("at", t, position)],
            var2n[("do", t, a)],
            -var2n[("block", t, c[0])],
            var2n[("block", t + 1, c[0])],
        ]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if c[0] in cells
    ]

    # les blocks non adjacent restent à leur place
    clauses += [
        [
            -var2n[("at", t, position)],
            -var2n[("block", t, cell)],
            var2n[("block", t + 1, cell)],
        ]
        for t in range(t_max)
        for cell in cells
        if not (cell in adjacent(position))
    ]

    # des blocks n'aparaissent pas si l'action n'est pas push_block
    for a in ACTIONS:
        if a not in pushing_action:
            clauses += [
                [
                    -var2n[("do", t, a)],
                    var2n[("block", t, cell)],
                    -var2n[("block", t + 1, cell)],
                ]
                for t in range(t_max)
                for cell in cells
            ]

    # des blocks n'aparaissent pas dans une autre direction que le push si l'action est push_block
    for a in ACTIONS:
        if a in pushing_action:
            clauses += [
                [
                    -var2n[("do", t, a)],
                    -var2n[("at", t, position)],
                    var2n[("block", t, cell)],
                    -var2n[("block", t + 1, cell)],
                ]
                for t in range(t_max)
                for cell in cells
                if cell != WherePushed[a][1]
            ]

    # les blocks poussés dans un mur restent à leur place
    # c[0] correspond à case qu'on pousse, c[1] la destination
    clauses += [
        [
            -var2n[("at", t, position)],
            -var2n[("do", t, a)],
            -var2n[("block", t, c[0])],
            var2n[("block", t + 1, c[0])],
        ]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if (not c[1] in cells) and (c[0] in cells)
    ]

    # les blocks poussés dans une case non vide restent à leur place
    # c[0] correspond à case qu'on pousse, c[1] la destination
    clauses += [
        [
            -var2n[("at", t, position)],
            -var2n[("do", t, a)],
            -var2n[("block", t, c[0])],
            var2n[("empty", t, c[1])],
            var2n[("block", t + 1, c[0])],
        ]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if (c[0] in cells) and (c[1] in cells)
    ]

    # les blocks poussés dans une case vide changent de place
    # c[0] correspond à case qu'on pousse, c[1] la destination
    clauses += [
        [
            -var2n[("at", t, position)],
            -var2n[("do", t, a)],
            -var2n[("block", t, c[0])],
            -var2n[("empty", t, c[1])],
            var2n[("block", t + 1, c[1])],
        ]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if (c[0] in cells) and (c[1] in cells)
    ]

    # les blocks qui ont changés de place ne sont plus au même endroit
    # c[0] correspond à case qu'on pousse, c[1] la destination
    clauses += [
        [
            -var2n[("at", t, position)],
            -var2n[("do", t, a)],
            -var2n[("block", t, c[0])],
            -var2n[("empty", t, c[1])],
            -var2n[("block", t + 1, c[0])],
        ]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if (c[0] in cells) and (c[1] in cells)
    ]

    # on ne peut pas traverser les blocks
    clauses += [
        [-var2n[("at", t, position)], -var2n[("do", t, a)], -var2n[("block", t, c)]]
        for t in range(t_max)
        for a, c in Move.items()
        if (c in cells)
    ]

    return clauses


def clauses_mobs(
    var2n: dict, t_max: int, cells: List[Coord], position: Coord
) -> List[Clause]:
    """
    :param var2n: dict giving the corresponding number for each variable
    :param t_max: horizon
    :param cells: list of all cells coords
    :param position: cell position
    :return: clauses corresponding to mobs
    """
    pushing_action = ("push_mob_left", "push_mob_right", "push_mob_up", "push_mob_down")
    moving_action = ("left", "right", "up", "down")

    WherePushed = {a: where_pushed(position, a) for a in pushing_action}
    Move = {a: succ(position, a) for a in moving_action}

    clauses = []

    # PRECONDITIONS OF PUSHING
    # interdit de push_mob une cellule qui n'est pas mob
    clauses += [
        [-var2n[("at", t, position)], var2n[("mob", t, c[0])], -var2n[("do", t, a)]]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if c[0] in cells
    ]

    # interdit de push_mob dans un mur
    clauses += [
        [-var2n[("at", t, position)], -var2n[("do", t, a)]]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if not (c[0] in cells)
    ]

    # EVOLUTIONS OF MOBS
    # les mobs non push restent à leur place si la case ne devient pas un spike
    clauses += [
        [
            -var2n[("at", t, position)],
            var2n[("do", t, a)],
            -var2n[("mob", t, c[0])],
            var2n[("spike", t + 1, c[0])],
            var2n[("mob", t + 1, c[0])],
        ]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if c[0] in cells
    ]

    # les mobs non adjacent restent à leur place si la case ne devient pas un spike
    clauses += [
        [
            -var2n[("at", t, position)],
            -var2n[("mob", t, cell)],
            var2n[("spike", t + 1, cell)],
            var2n[("mob", t + 1, cell)],
        ]
        for t in range(t_max)
        for cell in cells
        if not (cell in adjacent(position))
    ]

    # des mobs n'aparaissent pas si l'action n'est pas push_mob
    for a in ACTIONS:
        if a not in pushing_action:
            clauses += [
                [
                    -var2n[("do", t, a)],
                    var2n[("mob", t, cell)],
                    -var2n[("mob", t + 1, cell)],
                ]
                for t in range(t_max)
                for cell in cells
            ]

    # des mobs n'aparaissent pas dans une autre direction que le push si l'action est push_mob
    for a in ACTIONS:
        if a in pushing_action:
            clauses += [
                [
                    -var2n[("do", t, a)],
                    -var2n[("at", t, position)],
                    var2n[("mob", t, cell)],
                    -var2n[("mob", t + 1, cell)],
                ]
                for t in range(t_max)
                for cell in cells
                if cell != WherePushed[a][1]
            ]

    # les mobs poussés disparaissent
    # c[0] correspond à case qu'on pousse, c[1] la destination
    clauses += [
        [
            -var2n[("at", t, position)],
            -var2n[("do", t, a)],
            -var2n[("mob", t, c[0])],
            -var2n[("mob", t + 1, c[0])],
        ]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if (c[0] in cells)
    ]

    # les mobs poussés sur une case vide qui n'est pas un spike ou un block se déplacent
    # c[0] correspond à case qu'on pousse, c[1] la destination
    clauses += [
        [
            -var2n[("at", t, position)],
            -var2n[("do", t, a)],
            var2n[("spike", t + 1, c[1])],
            var2n[("block", t, c[1])],
            var2n[("mob", t + 1, c[1])],
        ]
        for t in range(t_max)
        for a, c in WherePushed.items()
        if (c[1] in cells)
    ]

    # on ne peut pas traverser les mobs
    clauses += [
        [-var2n[("at", t, position)], -var2n[("do", t, a)], -var2n[("mob", t, c)]]
        for t in range(t_max)
        for a, c in Move.items()
        if (c in cells)
    ]

    return clauses


def level_data_to_clauses(data: dict) -> Tuple[dict, List[Clause]]:
    """
    :param data: dict containing all level data
    :return: all clauses corresponding to the level
    """
    coords = grid_to_coords_dict(data["grid"])
    t_max = data["max_steps"]
    var2n = vocabulary(coords, t_max)

    clauses = clauses_exactly_one_action(var2n, t_max) + clauses_initial_state(
        var2n, coords, t_max
    )

    for cell in coords["cells"]:
        clauses += clauses_successor_from_given_position(
            var2n, coords["cells"], t_max, cell
        )
        clauses += clauses_spikes(var2n, t_max, cell)
        clauses += clauses_empty(var2n, t_max, cell)
        clauses += clauses_blocks(var2n, t_max, coords["cells"], cell)
        clauses += clauses_mobs(var2n, t_max, coords["cells"], cell)

    for cell in coords["cells"]:
        if cell not in coords["lock"] + coords["demonesses"]:
            clauses += clauses_empty(var2n, t_max, cell)

    for cell in coords["traps_unsafe"] + coords["traps_safe"]:
        clauses += clauses_traps(var2n, t_max, cell)

    if len(coords["lock"]) > 0 and len(coords["key"]) > 0:
        clauses += clauses_lock_and_key(
            var2n, t_max, coords["lock"][0], coords["key"][0]
        )

    # on doit être à côté d'une demoness à la fin
    clauses.append(
        [
            var2n[("at", t_max, coord)]
            for demoness in coords["demonesses"]
            for coord in adjacent(demoness)
            if coord in coords["cells"]
        ]
    )

    return var2n, clauses


def clauses_to_dimacs(clauses: Set[Clause], numvar: int) -> str:
    """
    :param clauses: list of all clauses corresponding to the problem
    :param numvar: number of variables
    :return: string
    """
    dimacs = "c Helltaker SAT\np cnf " + str(numvar) + " " + str(len(clauses)) + "\n"
    for clause in clauses:
        for atom in clause:
            dimacs += str(atom) + " "
        dimacs += "0\n"
    return dimacs


def write_dimacs_file(dimacs: str, filename: str, encoding: str = "utf8"):
    """
    :param dimacs: file content
    :param filename: filename
    :param encoding: characters encoding
    :return: write cnf file in current directory
    """
    with open(filename, "w", newline="", encoding=encoding) as cnf:
        cnf.write(dimacs)


def exec_gophersat(filename: str, cmd: str = "./gophersat", encoding: str = "utf8"):
    """
    :param filename: name of cnf file
    :param cmd: command to run gophersat
    :param encoding: characters encoding
    :return: Sat (bool), Model (list)
    """
    result = subprocess.run(
        [cmd, filename], capture_output=True, check=True, encoding=encoding
    )
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:].split(" ")

    return True, [int(x) for x in model]


def exec_pysat(filename: str):
    """
    :param filename: name of cnf file
    :return: Sat (bool), Model (list)
    """
    from pysat.formula import CNF
    from pysat.solvers import Glucose4

    formula = CNF(from_file=filename)
    g = Glucose4()
    g.append_formula(formula)

    return g.solve(), g.get_model()


def sat_solving(data: dict, solver: str = 'gophersat'):
    """
    :param solver:
    :param data: dict containing all level data
    :return: a model if sat
    """
    v2n, clauses = level_data_to_clauses(data)
    n2v = {i: v for v, i in v2n.items()}

    unique_clauses = {tuple(c) for c in clauses}  # avoid equal clauses

    dimacs = clauses_to_dimacs(unique_clauses, len(v2n))
    filename = "helltaker.cnf"
    write_dimacs_file(dimacs, filename)

    if solver == 'gophersat':
        sat, model = exec_gophersat(filename)
    elif solver == 'pysat':
        sat, model = exec_pysat(filename)
    else:
        print('incorrect solver')
        return None

    if sat:
        return [n2v[i] for i in model if i > 0 and n2v[i][0] == "do"]

    print("pas de plan de taille", data["max_steps"])
    return None


def convert_model(sat_model: List):
    """
    :param sat_model: list of true variables "do" of the model
    :return: corresponding instructions (hbgd)
    """
    plan = ""
    for action in sat_model:
        plan += convert_action(action[2])
    return plan


def test():
    """
    Test function of SAT solving
    Run: python3 utils_asp.py ./levels/level1.txt
    """
    start = time()
    debug = False

    filename = sys.argv[1]
    grid_data = grid_from_file(filename)

    v2n, clauses = level_data_to_clauses(grid_data)
    n2v = {i: v for v, i in v2n.items()}

    if debug:
        for c in clauses:
            for a in c:
                if a > 0:
                    print(str(n2v.get(a)), end=" ")
                else:
                    print("-" + str(n2v.get(-a)), end=" ")
            print()

        print()

    model = sat_solving(grid_data, 'pysat')
    print(model)
    print(convert_model(model))

    print(f"\nRunning time: {time() - start}s")


if __name__ == "__main__":
    test()
