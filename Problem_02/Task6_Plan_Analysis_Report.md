# Problem 2: Mars Rover Sample Collection — Plan Analysis (Task 6)

Plans were generated with Fast Downward (greedy `eager_greedy([ff()])` = satisficing,
`astar(lmcut())` = optimal) and each was re-checked step by step with `simulate_plan.py`
(`Task4_goal_verification.txt`). All four reach the goal: all rocks at Base, both bays empty, rover at Base.

## 1. Plan lengths: satisficing vs optimal

| Scenario | Satisficing | Optimal | Difference |
|---|---|---|---|
| Base (5 rocks) | 30 | 25 | 5 actions longer |
| Extended (7 rocks, Base–SiteB closed) | 46 | 40 | 6 actions longer |

The greedy search stops at the first plan it finds and never compares round trips, so it takes
more of them: 4 Base trips (base) and 5 (extended). A* with LM-cut proves no shorter plan exists and
needs 3 and 4 trips. Each avoided trip saves about 5 to 6 actions, which accounts for the gap.
The extended scenario needs 15 more actions than the base optimum because two more rocks must be
fetched and every trip to SiteB/SiteD is a long detour.

## 2. How the optimal plan uses the two bays and when the drill is picked up

Base optimal (25 actions) uses three Base trips:
1. Rock2 (SiteB) in Bay1 and Rock4 (SiteD) in Bay2, both soft, delivered together (steps 1–8).
2. The drill is picked up at SiteE (step 12), then hard Rock5 (SiteF) goes in Bay1 and hard Rock3 (SiteC) in Bay2 on the way back (steps 13–21).
3. Rock1 (SiteA) alone, because nothing else is near it (steps 22–25).

Extended optimal (40 actions) uses four Base trips, and three of them fill both bays:
1. Rock4 (SiteD, Bay1) and Rock2 (SiteB, Bay2). On the way out the rover picks up the drill at SiteE (step 9).
2. Hard Rock5 and Rock7, both at SiteF, in Bay1 and Bay2.
3. Hard Rock3 (SiteC, Bay1) and soft Rock6 (SiteE, Bay2).
4. Rock1 (SiteA) alone.

The drill is picked up once and kept. In the base optimal plan it is picked up just before the first
hard rock is needed. In the extended optimal plan it is picked up at step 9, earlier than needed,
because the rover is already passing SiteE on its return from SiteB/SiteD, so it costs no extra moves.
The drill is only used from step 19 onward. The optimal plans never carry just one rock when a second
can be picked up on the same route.

## 3. Extended scenario: reaching SiteB and SiteD, and the one-way route

With Base–SiteB closed, SiteB and SiteD are only reachable by
Base → SiteA → SiteC → **SiteD** → SiteB. This is the only legal use of the one-way slope, in its
allowed direction SiteC → SiteD, and it appears in the optimal plan at step 3 (and once in the
satisficing plan, at step 16). Going back is not possible by the slope, since SiteD → SiteC is forbidden,
so the rover returns SiteB → SiteD → SiteE → SiteC → SiteA → Base (steps 7–12 of the optimal plan).
Reaching SiteB costs 4 moves in and 5 moves out (steps 7–12 include the drill pickup at SiteE), so the dust storm lengthens that trip a lot.

In the base scenario the slope is optional. The optimal plan never uses it and goes Base ↔ SiteB ↔ SiteD
directly. The 30-action satisficing plan uses it once (step 15), a locally convenient step that
contributes to its extra trip.
