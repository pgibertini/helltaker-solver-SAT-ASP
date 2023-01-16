
%%% MAP DESCRIPTION
#const horizon=33.
cell(1, 5).
cell(2, 4).
cell(2, 5).
cell(2, 6).
cell(3, 4).
cell(3, 5).
cell(3, 6).
cell(4, 2).
cell(4, 4).
cell(4, 5).
cell(4, 6).
cell(4, 8).
cell(5, 1).
cell(5, 2).
cell(5, 3).
cell(5, 4).
cell(5, 5).
cell(5, 6).
cell(5, 7).
cell(5, 8).
cell(5, 9).
cell(6, 1).
cell(6, 2).
cell(6, 3).
cell(6, 4).
cell(6, 5).
cell(6, 6).
cell(6, 7).
cell(6, 8).
cell(6, 9).
cell(7, 2).
cell(7, 3).
cell(7, 4).
cell(7, 5).
cell(7, 6).
cell(7, 7).
cell(7, 8).
demoness(1, 5).
key(5, 9).
fluent(lock(3, 5), 0).
fluent(block(3, 4), 0).
fluent(block(3, 6), 0).
fluent(block(4, 2), 0).
fluent(block(4, 4), 0).
fluent(block(5, 1), 0).
fluent(block(5, 4), 0).
fluent(block(5, 5), 0).
fluent(block(5, 6), 0).
fluent(block(6, 2), 0).
fluent(block(6, 3), 0).
fluent(block(6, 4), 0).
fluent(block(6, 7), 0).
fluent(block(6, 8), 0).
fluent(block(7, 4), 0).
fluent(block(7, 7), 0).
fluent(at(7, 2), 0).

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
