%% ====================================================================
%%  ROYAL ARCHIVE ACCESS VERIFICATION USING RESOLUTION REFUTATION
%%  Goal: prove  trusted(mira)
%%
%%  PREDICATES                       CONSTANTS     VARIABLES
%%    archivist(P)     P is an archivist          mira       P, R
%%    verifies(P,R)    P verifies record R        scroll_7   (person, record)
%%    trusted(P)       P is trusted
%%    access(P,R)      P has access to R
%%    sealed(R)        R is sealed
%%    permitted(P,R)   P may inspect R
%%    inspects(P,R)    P inspects R
%%    finds_mark(P,R)  P finds a hidden mark in R
%%    in_archive(R)    R is stored in the royal archive
%%
%%  Formula connectives used in this file:
%%    all(V,F)  ex(V,F)  imp(A,B)  and(A,B)  or(A,B)  not(A)
%%  Clause literals:  pos(Atom)  /  neg(Atom)
%% ====================================================================


%% --------------------------------------------------------------------
%% STEP 1: Predicate logic representation
%%         fol(Id, Description, Formula)
%% --------------------------------------------------------------------
fol(1, 'Every archivist who verifies a record is trusted',
    all(X, all(R,
        imp(and(archivist(X), verifies(X,R)), trusted(X))))).

fol(2, 'Every trusted person with access to a sealed record is permitted to inspect it',
    all(X, all(R,
        imp(and(and(trusted(X), access(X,R)), sealed(R)), permitted(X,R))))).

fol(3, 'Anyone who inspects a record and finds a hidden mark in it verifies it',
    all(X, all(R,
        imp(and(inspects(X,R), finds_mark(X,R)), verifies(X,R))))).

fol(4, 'Every record stored in the royal archive is sealed',
    all(R, imp(in_archive(R), sealed(R)))).

fol(5, 'scroll_7 is stored in the royal archive',
    in_archive(scroll_7)).

fol(6, 'Mira has access to scroll_7',
    access(mira, scroll_7)).

fol(7, 'Mira inspects scroll_7 and finds a hidden mark in it',
    and(inspects(mira, scroll_7), finds_mark(mira, scroll_7))).

fol(8, 'Mira is an archivist',
    archivist(mira)).

% The goal to be proved
goal(trusted(mira)).


%% --------------------------------------------------------------------
%% STEP 2: Negation of the goal (added to the knowledge base)
%% --------------------------------------------------------------------
negated_goal(not(G)) :- goal(G).


%% --------------------------------------------------------------------
%% STEP 3: Implication removal      (A -> B)  becomes  (~A v B)
%% --------------------------------------------------------------------
rem_imp(imp(A,B), or(not(A1),B1)) :- !, rem_imp(A,A1), rem_imp(B,B1).
rem_imp(and(A,B), and(A1,B1))     :- !, rem_imp(A,A1), rem_imp(B,B1).
rem_imp(or(A,B),  or(A1,B1))      :- !, rem_imp(A,A1), rem_imp(B,B1).
rem_imp(not(A),   not(A1))        :- !, rem_imp(A,A1).
rem_imp(all(V,F), all(V,F1))      :- !, rem_imp(F,F1).
rem_imp(ex(V,F),  ex(V,F1))       :- !, rem_imp(F,F1).
rem_imp(A, A).


%% --------------------------------------------------------------------
%% STEP 4: Move negation inward (De Morgan, quantifier duality,
%%         double negation) -> negation normal form
%% --------------------------------------------------------------------
nnf(not(not(A)),    B)       :- !, nnf(A, B).
nnf(not(and(A,B)),  or(A1,B1))  :- !, nnf(not(A), A1), nnf(not(B), B1).
nnf(not(or(A,B)),   and(A1,B1)) :- !, nnf(not(A), A1), nnf(not(B), B1).
nnf(not(all(V,F)),  ex(V,F1))   :- !, nnf(not(F), F1).
nnf(not(ex(V,F)),   all(V,F1))  :- !, nnf(not(F), F1).
nnf(and(A,B),       and(A1,B1)) :- !, nnf(A, A1), nnf(B, B1).
nnf(or(A,B),        or(A1,B1))  :- !, nnf(A, A1), nnf(B, B1).
nnf(all(V,F),       all(V,F1))  :- !, nnf(F, F1).
nnf(ex(V,F),        ex(V,F1))   :- !, nnf(F, F1).
nnf(A, A).


%% --------------------------------------------------------------------
%% STEP 5: Standardize variables apart
%%         Each fol/3 solution is read with its own fresh variables, so
%%         no two formulas share a variable.  When printing, every
%%         formula gets its own range of variable names (A,B / C,D / ...)
%%         via the 'Off' (offset) value.
%% --------------------------------------------------------------------
all_disjoint(Fs) :-
    findall(N, ( member(F, Fs), term_variables(F, Vs), length(Vs, N) ), Ns),
    sum_list(Ns, Total),
    term_variables(Fs, AllVars),
    length(AllVars, Total).


%% --------------------------------------------------------------------
%% STEP 6: Skolemization (and dropping universal quantifiers)
%%         ex(V,F) -> replace V by a Skolem constant / function of the
%%         enclosing universal variables.  K0/K is a counter for names.
%% --------------------------------------------------------------------
skolem(all(V,F), Vs, K0, K, G) :- !,
    skolem(F, [V|Vs], K0, K, G).
skolem(ex(V,F), Vs, K0, K, G) :- !,
    K1 is K0 + 1,
    atom_concat(sk, K1, Name),
    reverse(Vs, Args),
    (   Args == []
    ->  V = Name
    ;   V =.. [Name|Args]
    ),
    skolem(F, Vs, K1, K, G).
skolem(and(A,B), Vs, K0, K, and(A1,B1)) :- !,
    skolem(A, Vs, K0, K1, A1),
    skolem(B, Vs, K1, K, B1).
skolem(or(A,B), Vs, K0, K, or(A1,B1)) :- !,
    skolem(A, Vs, K0, K1, A1),
    skolem(B, Vs, K1, K, B1).
skolem(A, _, K, K, A).

has_ex(ex(_,_)).
has_ex(all(_,F))  :- has_ex(F).
has_ex(not(F))    :- has_ex(F).
has_ex(and(A,B))  :- ( has_ex(A) ; has_ex(B) ).
has_ex(or(A,B))   :- ( has_ex(A) ; has_ex(B) ).


%% --------------------------------------------------------------------
%% STEP 7: Conversion to CNF (distribute v over &) as clause lists.
%%         A clause is a list of literals pos(P) / neg(P).
%% --------------------------------------------------------------------
cnf(and(A,B), C) :- !, cnf(A, CA), cnf(B, CB), append(CA, CB, C).
cnf(or(A,B),  C) :- !, cnf(A, CA), cnf(B, CB), cross(CA, CB, C).
cnf(not(P),   [[neg(P)]]) :- !.
cnf(P,        [[pos(P)]]).

cross([], _, []).
cross([K1|Ks], CB, C) :-
    cross_one(K1, CB, C1),
    cross(Ks, CB, C2),
    append(C1, C2, C).

cross_one(_, [], []).
cross_one(K1, [K2|Ks], [K|Rest]) :-
    append(K1, K2, K),
    cross_one(K1, Ks, Rest).


%% --------------------------------------------------------------------
%% Processing every formula through steps 3-7.
%% Record: r(Id, Text, F0, F3, F4, F6, Clauses, Off)
%% --------------------------------------------------------------------
process_all([], _, _, []).
process_all([Id-Text-F0|T], Off, K0, [r(Id,Text,F0,F3,F4,F6,Cls,Off)|Rs]) :-
    rem_imp(F0, F3),
    nnf(F3, F4),
    skolem(F4, [], K0, K1, F6),
    cnf(F6, Cls),
    term_variables(F0, Vs),
    length(Vs, N),
    Off1 is Off + N,
    process_all(T, Off1, K1, Rs).


%% --------------------------------------------------------------------
%% Pretty printing (plain ASCII)
%% --------------------------------------------------------------------
pp_t(T) :- write_term(T, [numbervars(true), quoted(false)]).

pp(all(V,F))  :- !, write('forall '), pp_t(V), write(': '), pp(F).
pp(ex(V,F))   :- !, write('exists '), pp_t(V), write(': '), pp(F).
pp(imp(A,B))  :- !, write('('), pp(A), write(' -> '), pp(B), write(')').
pp(and(A,B))  :- !, write('('), pp(A), write(' & '),  pp(B), write(')').
pp(or(A,B))   :- !, write('('), pp(A), write(' v '),  pp(B), write(')').
pp(not(A))    :- !, write('~'), pp(A).
pp(A)         :- pp_t(A).

% show a formula, naming its variables from offset Off
show(F, Off) :-
    copy_term(F, G),
    numbervars(G, Off, _),
    pp(G).

pp_lit(pos(P)) :- !, pp_t(P).
pp_lit(neg(P)) :- write('~'), pp_t(P).

pp_lits([]).
pp_lits([L]) :- !, pp_lit(L).
pp_lits([L|Ls]) :- pp_lit(L), write(' v '), pp_lits(Ls).

pp_clause(C) :-
    (   C == []
    ->  write('[]   <-- EMPTY CLAUSE')
    ;   write('['), pp_lits(C), write(']')
    ).

show_clause(C, Off) :-
    copy_term(C, D),
    numbervars(D, Off, _),
    pp_clause(D).

line :-
    write('======================================================================'), nl.

banner(T) :-
    nl, line, write(T), nl, line.


%% --------------------------------------------------------------------
%% STEP 8: Resolution refutation
%%   Linear (input) resolution started from the negated goal, with
%%   iterative deepening so that the shortest proof is found.
%%   Each resolvent is recorded and printed afterwards.
%% --------------------------------------------------------------------
comp(neg(A), pos(B)) :- A = B.
comp(pos(A), neg(B)) :- A = B.

% res(CurLabel, CurClause, Depth, MaxDepth, KB, Steps)
res(_, Clause, _, _, _, []) :-
    Clause == [], !.
res(CurLab, Clause, Depth, Max, KB, [step(CurLab, KLab, Snap, NewLab)|Steps]) :-
    Depth < Max,
    select(L, Clause, R1),
    member(kb(KLab, _, _, Cl0), KB),
    copy_term(Cl0, Cl),                 % rename the KB clause apart
    select(L2, Cl, R2),
    comp(L, L2),                        % unify the complementary literals
    append(R1, R2, R0),
    list_to_set(R0, Res),
    copy_term(s(Clause, Cl, L, Res), Snap),
    D1 is Depth + 1,
    atom_concat('R', D1, NewLab),
    res(NewLab, Res, D1, Max, KB, Steps).

refutation(KB, GoalClause, Steps) :-
    between(1, 12, Max),
    res('NG', GoalClause, 0, Max, KB, Steps),
    !.

% Number the KB clauses C1, C2, ...  kb(Label, RuleId, Offset, Clause)
number_clauses(Rs, KB) :-
    findall(Id-Off-C,
            ( member(r(Id,_,_,_,_,_,Cls,Off), Rs), member(C, Cls) ),
            Triples),
    label_clauses(Triples, 1, KB).

label_clauses([], _, []).
label_clauses([Id-Off-C|T], N, [kb(L,Id,Off,C)|R]) :-
    atom_concat('C', N, L),
    N1 is N + 1,
    label_clauses(T, N1, R).


%% --------------------------------------------------------------------
%% MAIN  --  run with   ?- main.
%% --------------------------------------------------------------------
main :-
    findall(Id-Text-F, fol(Id, Text, F), Items),
    process_all(Items, 0, 0, Rs),
    goal(G),
    negated_goal(NG),
    rem_imp(NG, NG3),
    nnf(NG3, NG4),
    cnf(NG4, [NGClause]),

    banner('STEP 1: Predicate logic representation'),
    forall(member(r(Id,Text,F0,_,_,_,_,_), Rs),
           ( format('(~w) ~w~n      ', [Id, Text]), show(F0, 0), nl )),
    write('Goal to prove : '), pp(G), nl,

    banner('STEP 2: Negation of the goal (added to the KB)'),
    write('Negated goal  : '), pp(NG), nl,

    banner('STEP 3: Implication removal   (A -> B  becomes  ~A v B)'),
    forall(member(r(Id,_,_,F3,_,_,_,_), Rs),
           ( format('(~w) ', [Id]), show(F3, 0), nl )),
    write('(G) '), pp(NG3), nl,

    banner('STEP 4: Negation moved inward (negation normal form)'),
    forall(member(r(Id,_,_,_,F4,_,_,_), Rs),
           ( format('(~w) ', [Id]), show(F4, 0), nl )),
    write('(G) '), pp(NG4), nl,
    write('(No rule has a negation above &, v or a quantifier, so the'), nl,
    write(' formulas are already in negation normal form.)'), nl,

    banner('STEP 5: Standardization of variables (each formula gets its own)'),
    forall(member(r(Id,_,_,_,F4,_,_,Off), Rs),
           ( format('(~w) ', [Id]), show(F4, Off), nl )),
    findall(F, member(r(_,_,F,_,_,_,_,_), Rs), F0s),
    (   all_disjoint(F0s)
    ->  write('Check: no two formulas share a variable -> OK'), nl
    ;   write('Check FAILED: formulas share variables'), nl
    ),

    banner('STEP 6: Skolemization (and dropping universal quantifiers)'),
    forall(member(r(Id,_,_,_,_,F6,_,Off), Rs),
           ( format('(~w) ', [Id]), show(F6, Off), nl )),
    (   member(r(_,_,_,_,F4x,_,_,_), Rs), has_ex(F4x)
    ->  true
    ;   write('No existential quantifier occurs in the KB or in the negated'), nl,
        write('goal, so no Skolem constants/functions are needed.'), nl,
        write('Variables left over are implicitly universally quantified.'), nl
    ),

    banner('STEP 7: CNF clauses'),
    number_clauses(Rs, KB),
    forall(member(kb(L,Id,Off,C), KB),
           ( format('~w  (from rule ~w):  ', [L, Id]), show_clause(C, Off), nl )),
    write('NG  (negated goal):  '), show_clause(NGClause, 0), nl,

    banner('STEP 8: Resolution refutation'),
    (   refutation(KB, NGClause, Steps)
    ->  print_proof(KB, NGClause, Steps)
    ;   write('No refutation found: the goal does not follow.'), nl
    ).

print_proof(KB, NGClause, Steps) :-
    write('Start with the negated goal:'), nl,
    write('   NG : '), show_clause(NGClause, 0), nl, nl,
    forall(nth1(I, Steps, step(CurLab, KLab, Snap, NewLab)),
           print_step(I, CurLab, KLab, Snap, NewLab)),
    findall(K, member(step(_,K,_,_), Steps), Used0),
    sort(Used0, Used),
    findall(L, member(kb(L,_,_,_), KB), All),
    subtract(All, Used, Unused),
    length(Steps, NSteps),
    write('----------------------------------------------------------------------'), nl,
    format('RESULT: the empty clause [] was derived in ~w resolution steps.~n', [NSteps]),
    write('KB + ~trusted(mira) is contradictory, hence trusted(mira) follows. QED'), nl,
    format('Clauses used   : ~w~n', [Used]),
    format('Clauses unused : ~w~n', [Unused]).

print_step(I, CurLab, KLab, Snap, NewLab) :-
    copy_term(Snap, s(Cur, KC, L, Res)),
    numbervars(s(Cur, KC, L, Res), 0, _),
    format('Step ~w: resolve ~w with ~w on the literal ', [I, CurLab, KLab]),
    pp_lit(L), nl,
    format('   ~w : ', [CurLab]), pp_clause(Cur), nl,
    format('   ~w : ', [KLab]),   pp_clause(KC),  nl,
    format('   ==> ~w : ', [NewLab]), pp_clause(Res), nl, nl.
