# Helltaker Solver - ASPPLAN & SATPLAN
### Pierre Gibertini, Romane Dauge, Anne-Soline Guilbert--Ly
*This project has been realized in the context of a Problem Solving and Logic Programming course at UTC - Université de Technologie de Compiègne (France)*

*Given instructions* : https://hackmd.io/@ia02/BJ6eDYUI5
***

## 1. Presentation

**The goal of the project was to develop a program capable of solving Helltaker game levels.**

Example of level :

![Level 7](https://cdn.canardware.com/2021/05/05014910/6841-helltaker-1.jpg)

The goal of each level is to do a succession of actions (`up`, `down`, `left` or `right`) in order to reach the demon girl, in a given number of actions.

### Input

A simple `.txt` with a title in the first line, a maximum number of moves in the second line, then the description of the level. The lines do not have to be finished.

- `H`: hero
- `D`: demoness
- `#`: wall
- ` ` : empty
- `B`: block
- `K`: key
- `L`: lock
- `M`: mob (skeleton)
- `S`: spikes
- `T`: trap (safe)
- `U`: trap (unsafe)
- `O`: block on spike
- `P`: block on trap (safe)
- `Q`: block on trap (unsafe)

#### Example

```
Level 1
23
     ###
  ### H#
 #  M  #
 # M M#
#  ####
# B  B #
# B B  D#
#########
```

### Output

A list of insctructions to solve the level in-game. 
- `u`: up
- `d`: down
- `l`: left
- `r`: right

#### Example
Level #1 output: `dlllllllddlddrruurrrrdr`

## 2. Usage

Two different solving methods have been implemented.

### ASPPLAN

- https://en.wikipedia.org/wiki/Answer_set_programming

**Requirement:** `pip install clingo`

To solve a level with the ASPPLAN method:
> `python3 plan_asp.py path_to_file`

To print the ASP file and enumerate all the solutions to a given level!
> `python3 asp_utils.py path_to_file`

> Note: ASP solutions for each level are saved in the directory `asp_solutions` if you want to have a look at the strategies adopted.
> It is also possible to run the solving directly from the `.lp` file using `clingo levelX.lp -n0` command (`-n0` to generate all the solutions).

### SATPLAN

- https://en.wikipedia.org/wiki/Satplan

**Requirement:** `pip install python-sat`

To solve a level with the SATPLAN method:
> `python3 plan_sat.py path_to_file`

#### Example
`python3 plan_asp.py ../levels/level1.txt`

## 3. Experimental testing

#### Number of different solutions per level

| Level   | Number of solutions |
|---------|---------------------| 
| level 1 | 8                   |
| level 2 | 3                   |
| level 3 | 1                   |
| level 4 | 2                   |
| level 5 | 26                  |
| level 6 | 39                  |
| level 7 | 2                   |
| level 8 | 4                   |
| level 9 | 2                   |

We compared the execution time between our two solving methods : ASP (using Clingo) and SAT (using the Glucose4 solver)

> The measurements were made on a Lenovo Yoga Slim 7 laptop (plugged in) with an AMD Ryzen 7 4700U processor.

| Level   | Execution time SAT | Execution time  ASP |
|---------|--------------------|---------------------|
| level 1 | 0m3,621s           | 0m0,717s            |
| level 2 | 0m2,108s           | 0m0,750s            |
| level 3 | 0m2,731s           | 0m2,082s            |
| level 4 | 0m2,384s           | 0m0,771s            |
| level 5 | 0m1,675s           | 0m0,662s            |
| level 6 | 0m11,511s          | 0m15,219s           |
| level 7 | 0m3,467s           | 0m7,317s            |
| level 8 | 0m6,221s           | 0m0,121s            |
| level 9 | 0m11,176s          | 0m4,100s            |

In general, our approach in ASP is more efficient. 
In addition, the ASP language allows a shorter and more readable program than SAT, and is much easier to understand.

## 4. More details
Link to the project report hosted on HackMD :
https://hackmd.io/@Romane/ryn--SMKq

*The report (written in French) contains a lot of details about our approach and the solving strategies used*

## 5. ASP example

The following ASP example allows the solving of the first level.

```
%%% MAP DESCRIPTION
#const horizon=23.
cell(0, 0).
cell(0, 1).
cell(0, 2).
cell(0, 3).
cell(0, 4).
cell(0, 8).
cell(1, 0).
cell(1, 1).
cell(1, 5).
cell(1, 6).
cell(1, 8).
cell(2, 0).
cell(2, 2).
cell(2, 3).
cell(2, 4).
cell(2, 5).
cell(2, 6).
cell(2, 8).
cell(3, 0).
cell(3, 2).
cell(3, 3).
cell(3, 4).
cell(3, 5).
cell(3, 7).
cell(3, 8).
cell(4, 1).
cell(4, 2).
cell(4, 7).
cell(4, 8).
cell(5, 1).
cell(5, 2).
cell(5, 3).
cell(5, 4).
cell(5, 5).
cell(5, 6).
cell(5, 8).
cell(6, 1).
cell(6, 2).
cell(6, 3).
cell(6, 4).
cell(6, 5).
cell(6, 6).
cell(6, 7).
demoness(6, 7).
fluent(block(5, 2), 0).
fluent(block(5, 5), 0).
fluent(block(6, 2), 0).
fluent(block(6, 4), 0).
fluent(mob(2, 4), 0).
fluent(mob(3, 3), 0).
fluent(mob(3, 5), 0).
fluent(at(1, 6), 0).

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
```
