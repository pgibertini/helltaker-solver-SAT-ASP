# Helltaker Solver - ASPPLAN & SATPLAN
### Pierre Gibertini, Romane Dauge, Anne-Soline Guilbert--Ly
*This project has been realized in the context of a Problem Solving and Logic Programming course at UTC - Université de Technologie de Compiègne (France)*

*Given instructions* : https://hackmd.io/@ia02/BJ6eDYUI5
***

## 1. Presentation

**The goal of the project was to develop a program capable of solving Helltaker game levels.**

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

To solve a level with the ASPPLAN method:
> python3 plan_asp.py path_to_file


### SATPLAN

- https://en.wikipedia.org/wiki/Satplan

To solve a level with the SATPLAN method:
> python3 plan_sat.py path_to_file

#### Example
`python3 plan_asp.py ../levels/level1.txt`

## 3. Experimental testing

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