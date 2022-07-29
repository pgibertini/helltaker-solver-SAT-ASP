"""
Version: 1.1.1
Auteur : Sylvain Lagrue <sylvain.lagrue@hds.utc.fr>

Ce module contient différentes fonction permettant de lire des fichiers Helltaker au format défini pour le projet et de vérifier des plans.
"""

from pprint import pprint
import sys
from typing import List


def complete(m: List[List[str]], n: int):
    for l in m:
        for _ in range(len(l), n):
            l.append(" ")
    return m


def convert(grid: List[List[str]], voc: dict):
    new_grid = []
    for line in grid:
        new_line = []
        for char in line:
            if char in voc:
                new_line.append(voc[char])
            else:
                new_line.append(char)
        new_grid.append(new_line)
    return new_grid


def grid_from_file(filename: str, voc: dict = {}):
    """
    Cette fonction lit un fichier et le convertit en une grille de Helltaker

    Arguments:
    - filename: fichier contenant la description de la grille
    - voc: argument facultatif permettant de convertir chaque case de la grille en votre propre vocabulaire

    Retour:
    - un dictionnaire contenant:
        - la grille de jeu sous une forme d'une liste de liste de (chaînes de) caractères
        - le nombre de ligne m
        - le nombre de colonnes n
        - le titre de la grille
        - le nombre maximal de coups max_steps
    """

    grid = []
    m = 0  # nombre de lignes
    n = 0  # nombre de colonnes
    no = 0  # numéro de ligne du fichier
    title = ""
    max_steps = 0

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            no += 1

            l = line.rstrip()

            if no == 1:
                title = l
                continue
            if no == 2:
                max_steps = int(l)
                continue

            if len(l) > n:
                n = len(l)
                complete(grid, n)

            if l != "":
                grid.append(list(l))
    if voc:
        grid = convert(grid, voc)

    m = len(grid)

    return {"grid": grid, "title": title, "m": m, "n": n, "max_steps": max_steps}


def check_plan(plan: str):
    """
    Cette fonction vérifie que votre plan est valide/

    Argument: un plan sous forme de chaîne de caractères
    Retour  : True si le plan est valide, False sinon
    """
    valid = "udlr"
    for c in plan:
        if c not in valid:
            return False
    return True


def convert_action(action: str) -> str:
    """
    :param action: an action such as defined in the vocabulary
    :return: corresponding directions (hbgd)
    """
    if action in ["up", "push_block_up", "push_mob_up"]:
        return "u"
    if action in ["down", "push_block_down", "push_mob_down"]:
        return "d"
    if action in ["left", "push_block_left", "push_mob_left"]:
        return "l"
    if action in ["right", "push_block_right", "push_mob_right"]:
        return "r"

    return ""


def test():
    if len(sys.argv) != 2:
        sys.exit(-1)

    filename = sys.argv[1]

    pprint(grid_from_file(filename, {"H": "@", "B": "$", "D": "."}))

    print(check_plan("erfre"))
    print(check_plan("uuddlrdr"))


if __name__ == "__main__":
    test()
