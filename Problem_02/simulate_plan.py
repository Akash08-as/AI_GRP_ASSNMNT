#!/usr/bin/env python3
"""
Task 4 -- independent plan validator / step-by-step simulator (VAL substitute).

Reads the initial state and goal directly from a PDDL problem file, replays a
plan file action by action using the STRIPS semantics of Domain.pddl, prints
the state change after every step, and checks the goal at the end.
Case-insensitive (Fast Downward prints siteA, the PDDL files use SiteA);
lines starting with ';' (e.g. "; cost = 40 (unit cost)") are ignored.

Usage:
    python3 simulate_plan.py <problem.pddl> <plan_file>
Example:
    python3 simulate_plan.py Problem_extended.pddl Problem_extended_optimal.soln
"""
import re
import sys


def tokenize(text):
    text = re.sub(r";[^\n]*", "", text)
    return re.findall(r"\(|\)|[^\s()]+", text.lower())


def parse_sexp(tokens):
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            done = stack.pop()
            stack[-1].append(done)
        else:
            stack[-1].append(t)
    return stack[0]


def section(sexp, key):
    for item in sexp[0]:
        if isinstance(item, list) and item and item[0] == key:
            return item[1:]
    return []


def load_problem(path):
    sexp = parse_sexp(tokenize(open(path).read()))
    init = {tuple(f) for f in section(sexp, ":init")}
    goal_expr = section(sexp, ":goal")[0]
    goal = [tuple(g) for g in goal_expr[1:]] if goal_expr[0] == "and" else [tuple(goal_expr)]
    return init, goal


def apply_action(state, line):
    p = line.strip("()").split()
    act, args = p[0], p[1:]
    fail = lambda why: (_ for _ in ()).throw(AssertionError(f"({line}) -- {why}"))
    need = lambda fact, why: fact in state or fail(why)

    if act == "move":
        r, a, b = args
        need(("at", r, a), f"rover not at {a}")
        need(("connected", a, b), f"no route {a} -> {b}")
        state.discard(("at", r, a)); state.add(("at", r, b))
    elif act == "pick-drill":
        r, d, l = args
        need(("at", r, l), f"rover not at {l}")
        need(("drill-at", d, l), f"{d} not at {l}")
        state.discard(("drill-at", d, l)); state.add(("has-drill", r, d))
    elif act == "collect-soft":
        r, rk, l, b = args
        need(("at", r, l), f"rover not at {l}")
        need(("rock-at", rk, l), f"{rk} not at {l}")
        need(("soft", rk), f"{rk} is not soft")
        need(("bay-empty", b), f"{b} not empty")
        state.discard(("rock-at", rk, l)); state.discard(("bay-empty", b)); state.add(("in-bay", rk, b))
    elif act == "collect-hard":
        r, rk, l, b, d = args
        need(("at", r, l), f"rover not at {l}")
        need(("rock-at", rk, l), f"{rk} not at {l}")
        need(("hard", rk), f"{rk} is not hard")
        need(("bay-empty", b), f"{b} not empty")
        need(("has-drill", r, d), "rover is not carrying the drill")
        state.discard(("rock-at", rk, l)); state.discard(("bay-empty", b)); state.add(("in-bay", rk, b))
    elif act == "deposit":
        r, rk, l, b = args
        need(("at", r, l), f"rover not at {l}")
        need(("in-bay", rk, b), f"{rk} not in {b}")
        state.discard(("in-bay", rk, b)); state.add(("bay-empty", b)); state.add(("rock-at", rk, l))
    else:
        fail("unknown action")


def run(problem_path, plan_path):
    state, goal = load_problem(problem_path)
    lines = [l.strip() for l in open(plan_path).read().lower().splitlines()
             if l.strip() and not l.strip().startswith(";")]
    print("=" * 72)
    print(f"Problem: {problem_path}\nPlan   : {plan_path}\n" + "=" * 72)
    for i, line in enumerate(lines, 1):
        apply_action(state, line)
        print(f"  step {i:2d}: {line}")
    print(f"\n  Total actions executed: {len(lines)}")

    print("\n  --- Final state ---")
    rover_loc = [f[2] for f in state if f[0] == "at"]
    print(f"  Rover at              : {rover_loc}")
    print(f"  Rocks at base         : {sorted(f[1] for f in state if f[0]=='rock-at' and f[2]=='base')}")
    print(f"  Empty bays            : {sorted(f[1] for f in state if f[0]=='bay-empty')}")
    print(f"  Rocks still in bays   : {sorted(f[1] for f in state if f[0]=='in-bay')}")
    print("\n  --- Goal check ---")
    ok = True
    for g in goal:
        hit = g in state
        ok &= hit
        print(f"  {'(' + ' '.join(g) + ')':38s} {'SATISFIED' if hit else 'NOT SATISFIED'}")
    print(f"\n  GOAL SATISFIED: {ok}   (plan length = {len(lines)})\n")
    return ok, len(lines)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    ok, _ = run(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
