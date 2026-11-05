#!/usr/bin/env python3
"""
Problem 1 - Smart Home Energy Consumption Analysis using Bayesian Networks
==========================================================================
Parts A-E of Group Assignment 2.

Implementation of the expert Bayesian network, inference, sampling, and
parameter learning for Problem 1.

Run this file with: python bn_energy.py
Required packages: numpy, pandas, networkx, matplotlib
"""
import itertools
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 42
SIZES = [500, 5000, 20000]
ESS = 10  # BDeu equivalent sample size


def log(*args):
    print(*args)


def section(title):
    log("\n" + "=" * 78)
    log(title)
    log("=" * 78)


# ---------------------------------------------------------------------------
# 1. Network definition (structure + expert CPTs)
# ---------------------------------------------------------------------------
STATES = {
    "W": ["Hot", "Mild", "Cold"],
    "D": ["Weekday", "Weekend"],
    "O": ["High", "Low"],
    "A": ["On", "Off"],
    "L": ["Heavy", "Light"],
    "E": ["High", "Low"],
}
NAMES = {"W": "Weather", "D": "DayType", "O": "Occupancy",
         "A": "AC", "L": "ApplianceLoad", "E": "EnergyConsumption"}
PARENTS = {"W": (), "D": (), "O": ("D",), "A": ("W", "O"), "L": ("O",), "E": ("A", "L")}
ORDER = ["W", "D", "O", "A", "L", "E"]  # a topological order


def expert_cpts():
    """CPT[var][parent_state_tuple] = list of probabilities in the order of STATES[var]."""
    c = {}
    c["W"] = {(): [0.50, 0.30, 0.20]}
    c["D"] = {(): [0.70, 0.30]}
    pO = {"Weekday": 0.45, "Weekend": 0.80}
    c["O"] = {(d,): [p, 1 - p] for d, p in pO.items()}
    pA = {("Hot", "High"): 0.90, ("Hot", "Low"): 0.60, ("Mild", "High"): 0.40,
          ("Mild", "Low"): 0.15, ("Cold", "High"): 0.10, ("Cold", "Low"): 0.05}
    c["A"] = {k: [p, 1 - p] for k, p in pA.items()}
    pL = {"High": 0.75, "Low": 0.35}
    c["L"] = {(o,): [p, 1 - p] for o, p in pL.items()}
    pE = {("On", "Heavy"): 0.92, ("On", "Light"): 0.68,
          ("Off", "Heavy"): 0.55, ("Off", "Light"): 0.12}
    c["E"] = {k: [p, 1 - p] for k, p in pE.items()}
    return c


def parent_configs(v):
    return list(itertools.product(*[STATES[p] for p in PARENTS[v]]))


def verify_cpts(cpts, label="CPT"):
    """Every row must be a valid distribution; every parent configuration must be present."""
    ok = True
    for v in ORDER:
        for cfg in parent_configs(v):
            if cfg not in cpts[v]:
                log(f"  [FAIL] {label}: {NAMES[v]} missing parent configuration {cfg}")
                ok = False
                continue
            row = np.array(cpts[v][cfg], dtype=float)
            if len(row) != len(STATES[v]) or (row < -1e-12).any() or (row > 1 + 1e-12).any() \
                    or abs(row.sum() - 1) > 1e-9:
                log(f"  [FAIL] {label}: {NAMES[v]} | {cfg} -> {row} (sum={row.sum():.12f})")
                ok = False
    return ok


# ---------------------------------------------------------------------------
# 2. Exact inference by enumeration over the joint
# ---------------------------------------------------------------------------
def joint_table(cpts):
    """Return dict {(w,d,o,a,l,e): probability} using the chain-rule factorisation."""
    J = {}
    for s in itertools.product(*[STATES[v] for v in ORDER]):
        a = dict(zip(ORDER, s))
        p = 1.0
        for v in ORDER:
            cfg = tuple(a[q] for q in PARENTS[v])
            p *= cpts[v][cfg][STATES[v].index(a[v])]
        J[s] = p
    return J


def prob(J, event):
    """P(event) where event = {var: state}."""
    idx = {v: i for i, v in enumerate(ORDER)}
    return sum(p for s, p in J.items() if all(s[idx[v]] == x for v, x in event.items()))


def cond(J, target, evidence):
    """P(target | evidence); NaN when the evidence has probability zero."""
    pe = prob(J, evidence) if evidence else 1.0
    if pe <= 0:
        return float("nan")
    return prob(J, {**evidence, **target}) / pe


QUERIES = [
    ("Q1", "P(E=High)",                              {"E": "High"}, {}),
    ("Q2", "P(E=High | W=Hot)",                      {"E": "High"}, {"W": "Hot"}),
    ("Q3", "P(E=High | D=Weekend)",                  {"E": "High"}, {"D": "Weekend"}),
    ("Q4", "P(E=High | W=Cold, O=High)",             {"E": "High"}, {"W": "Cold", "O": "High"}),
    ("Q5", "P(W=Hot | E=High)",                      {"W": "Hot"},  {"E": "High"}),
    ("Q6", "P(A=On | E=High)",                       {"A": "On"},   {"E": "High"}),
    ("Q7", "P(A=On | E=High, L=Heavy)",              {"A": "On"},   {"E": "High", "L": "Heavy"}),
]


def run_queries(cpts):
    J = joint_table(cpts)
    return [cond(J, t, e) for _, _, t, e in QUERIES]


# ---------------------------------------------------------------------------
# 3. Ancestral sampling (written by hand)
# ---------------------------------------------------------------------------
def ancestral_sample(cpts, n, seed):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        a = {}
        for v in ORDER:                       # topological order: parents before children
            cfg = tuple(a[q] for q in PARENTS[v])
            a[v] = STATES[v][rng.choice(len(STATES[v]), p=cpts[v][cfg])]
        rows.append(a)
    return pd.DataFrame(rows, columns=ORDER)


# ---------------------------------------------------------------------------
# 4. Parameter learning: MLE and BDeu (written by hand)
# ---------------------------------------------------------------------------
def learn_cpts(df, method, ess=ESS):
    """method in {'mle','bdeu'}. Returns (cpts, number_of_unseen_parent_configs)."""
    out, unseen = {}, 0
    for v in ORDER:
        r = len(STATES[v])
        cfgs = parent_configs(v)
        q = len(cfgs)
        out[v] = {}
        for cfg in cfgs:
            mask = np.ones(len(df), dtype=bool)
            for p, s in zip(PARENTS[v], cfg):
                mask &= (df[p].values == s)
            sub = df[v].values[mask]
            counts = np.array([(sub == s).sum() for s in STATES[v]], dtype=float)
            n = counts.sum()
            if method == "mle":
                if n == 0:            # MLE undefined -> fall back to uniform, and report it
                    unseen += 1
                    out[v][cfg] = [1.0 / r] * r
                else:
                    out[v][cfg] = list(counts / n)
            else:                      # BDeu: pseudo-count ess/(r*q) per cell
                alpha = ess / (r * q)
                out[v][cfg] = list((counts + alpha) / (n + ess / q))
    return out, unseen


# ---------------------------------------------------------------------------
# helpers for display
# ---------------------------------------------------------------------------
def ac_table(cpts_dict):
    return {cfg: cpts_dict["A"][cfg][0] for cfg in parent_configs("A")}



# ===========================================================================
# MAIN
# ===========================================================================
def main():
    section("PART A - EXPERT BAYESIAN NETWORK")
    cpts = expert_cpts()

    log("\nA.1/A.2  Structure: " + ", ".join(f"{p}->{v}" for v in ORDER for p in PARENTS[v]))
    log("\nA.2  CPT verification (each parent configuration must sum to 1):")
    ok = verify_cpts(cpts, "expert")
    n_rows = sum(len(parent_configs(v)) for v in ORDER)
    log(f"  Checked {n_rows} CPT rows across {len(ORDER)} variables -> {'ALL VALID' if ok else 'ERRORS FOUND'}")
    J = joint_table(cpts)
    log(f"  Sum of the full joint over {len(J)} states = {sum(J.values()):.12f}")
    assert ok and abs(sum(J.values()) - 1) < 1e-9

    # --- A.3 visualisation of the network
    G = nx.DiGraph()
    G.add_nodes_from(ORDER)
    G.add_edges_from((p, v) for v in ORDER for p in PARENTS[v])
    pos = {"W": (0, 3), "D": (4, 3), "O": (4, 2), "A": (2, 1), "L": (6, 1), "E": (4, 0)}
    labels = {v: f"{NAMES[v]}\n({v})\n" + "/".join(STATES[v]) for v in ORDER}
    fig, ax = plt.subplots(figsize=(9, 6.5))
    nx.draw_networkx_nodes(G, pos, node_size=5200, node_color="#cfe3f5", edgecolors="#2c5d8a", ax=ax)
    nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=22, node_size=5200, width=1.8,
                           edge_color="#444", ax=ax)
    ax.set_title("Smart-home energy Bayesian network (expert structure)")
    ax.set_xlim(-1.5, 7.5); ax.set_ylim(-0.8, 3.8); ax.axis("off")
    fig.tight_layout(); fig.savefig("network_structure.png", dpi=150); plt.close(fig)
    log("\nA.3  Network diagram created.")

    # --- A.4 queries
    log("\nA.4  Inference results (exact, by enumeration over the joint):")
    expert_vals = run_queries(cpts)
    for (qid, txt, _, _), v in zip(QUERIES, expert_vals):
        log(f"  {qid}: {txt:<34s} = {v:.6f}")

    # --- A.5 explaining away
    q6, q7 = expert_vals[5], expert_vals[6]
    log("\nA.5  Explaining away (Q6 vs Q7):")
    log(f"  Q6  P(AC=On | E=High)                  = {q6:.6f}")
    log(f"  Q7  P(AC=On | E=High, Load=Heavy)      = {q7:.6f}")
    log(f"  Change Q7 - Q6                         = {q7 - q6:+.6f}")
    log("  Interpretation: AC and Appliance Load are two competing causes of High energy.")
    log("  Observing High energy raises belief in each cause. Once we ALSO learn the load is")
    log("  Heavy, that cause already explains much of the high consumption, so the evidence")
    log("  for the AC being On is partly 'explained away' and its probability drops.")
    # supporting number: prior of AC for reference
    pa = prob(J, {"A": "On"})
    log(f"  (Reference: prior P(AC=On) = {pa:.6f}; P(AC=On | Load=Heavy) = "
        f"{cond(J, {'A': 'On'}, {'L': 'Heavy'}):.6f})")

    # --- A.6 hand calculation of Q1
    log("\nA.6  Hand calculation of Q1 = P(E=High), step by step (all numbers from the CPTs):")
    pW = dict(zip(STATES["W"], cpts["W"][()]))
    pD = dict(zip(STATES["D"], cpts["D"][()]))
    pOgD = {d: cpts["O"][(d,)][0] for d in STATES["D"]}               # P(O=High|D)
    pO_high = sum(pD[d] * pOgD[d] for d in pD)
    log(f"  Step 1: P(O=High) = {pD['Weekday']}*{pOgD['Weekday']} + {pD['Weekend']}*{pOgD['Weekend']}"
        f" = {pO_high:.4f};  P(O=Low) = {1 - pO_high:.4f}")
    pO = {"High": pO_high, "Low": 1 - pO_high}
    pAon_gO = {}
    for o in STATES["O"]:
        terms = [(pW[w], cpts["A"][(w, o)][0]) for w in STATES["W"]]
        pAon_gO[o] = sum(a * b for a, b in terms)
        expr = " + ".join(f"{a}*{b}" for a, b in terms)
        log(f"  Step 2: P(A=On | O={o}) = {expr} = {pAon_gO[o]:.4f}")
    # Joint of (A,L) via O:  P(A,L)=sum_O P(O)P(A|O)P(L|O)
    pAL = {}
    log("  Step 3: P(A,L) = sum_O P(O) P(A|O) P(L|O)")
    for a in STATES["A"]:
        for l in STATES["L"]:
            tot, parts = 0.0, []
            for o in STATES["O"]:
                pa_o = pAon_gO[o] if a == "On" else 1 - pAon_gO[o]
                pl_o = cpts["L"][(o,)][0] if l == "Heavy" else 1 - cpts["L"][(o,)][0]
                t = pO[o] * pa_o * pl_o
                parts.append(f"{pO[o]:.4f}*{pa_o:.4f}*{pl_o:.4f}")
                tot += t
            pAL[(a, l)] = tot
            log(f"     P(A={a:<3s}, L={l:<5s}) = " + " + ".join(parts) + f" = {tot:.6f}")
    log(f"     (check: sum of P(A,L) = {sum(pAL.values()):.6f})")
    total, parts = 0.0, []
    for (a, l), p in pAL.items():
        pe = cpts["E"][(a, l)][0]
        parts.append(f"{p:.6f}*{pe}")
        total += p * pe
    log("  Step 4: P(E=High) = sum_{A,L} P(A,L) P(E=High|A,L)")
    log("                    = " + " + ".join(parts))
    log(f"                    = {total:.6f}")
    log(f"  Code (Q1)         = {expert_vals[0]:.6f}   |difference| = {abs(total - expert_vals[0]):.2e}")
    assert abs(total - expert_vals[0]) < 1e-12
    log("  -> Hand calculation MATCHES the code result.")

    # ------------------------------------------------------------------ PART B
    section("PART B - CONDITIONAL INDEPENDENCE (d-separation)")
    if hasattr(nx, "is_d_separator"):
        dsep = lambda x, y, z: nx.is_d_separator(G, {x}, {y}, set(z))
    else:
        dsep = lambda x, y, z: nx.d_separated(G, {x}, {y}, set(z))

    tests = [
        ("1", "Weather _|_ DayType", "W", "D", [],
         "Only path W->A<-O<-D. A is a collider and neither A nor its descendant E is observed,"
         " so the path is blocked.",
         ({"W": "Hot"}, {}, {"D": "Weekend"}),
         "P(W=Hot)", "P(W=Hot | D=Weekend)"),
        ("2", "Weather _|_ DayType | EnergyConsumption", "W", "D", ["E"],
         "Path W->A<-O<-D: collider A has descendant E which is observed, so the collider is"
         " activated and the path is OPEN. Not d-separated.",
         ({"W": "Hot"}, {"E": "High"}, {"E": "High", "D": "Weekend"}),
         "P(W=Hot | E=High)", "P(W=Hot | E=High, D=Weekend)"),
        ("3", "Weather _|_ ApplianceLoad | Occupancy", "W", "L", ["O"],
         "Path W->A<-O->L: O is observed (fork) and A is an unobserved collider -> blocked."
         " Path W->A->E<-L: E is an unobserved collider -> blocked. All paths blocked.",
         ({"W": "Hot"}, {"O": "High"}, {"O": "High", "L": "Heavy"}),
         "P(W=Hot | O=High)", "P(W=Hot | O=High, L=Heavy)"),
    ]
    for num, stmt, x, y, z, why, (tgt, ev1, ev2), s1, s2 in tests:
        holds = dsep(x, y, z)
        a = cond(J, tgt, ev1) if ev1 else prob(J, tgt)
        b = cond(J, tgt, ev2)
        log(f"\nB.{num}  {stmt}")
        log(f"   d-separated (networkx): {holds}   -> independence {'HOLDS' if holds else 'DOES NOT HOLD'}")
        log(f"   Justification: {why}")
        log(f"   Numerical check: {s1} = {a:.6f}   vs   {s2} = {b:.6f}   (|diff| = {abs(a - b):.2e})")
        same = abs(a - b) < 1e-9
        log(f"   Numbers {'agree' if same else 'differ'} -> consistent with d-separation: {same == holds}")
        assert same == holds

    # ------------------------------------------------------------------ PART C
    section(f"PART C - SYNTHETIC DATA (ancestral sampling, seed = {SEED})")
    datasets = {}
    for n in SIZES:
        # Resetting the same seed makes the smaller dataset a prefix of the
        # larger dataset, which makes comparisons across sample sizes reproducible.
        df = ancestral_sample(cpts, n, SEED)
        datasets[n] = df
        df.to_csv(f"data_{n}.csv", index=False)
        log(f"\n--- Dataset of {n} samples (seed {SEED})")
        freq = df["W"].value_counts(normalize=True).reindex(STATES["W"])
        log("Empirical Weather frequencies (true: Hot 0.50, Mild 0.30, Cold 0.20):")
        for w in STATES["W"]:
            log(f"   {w:<5s} {freq[w]:.4f}")
        ct = pd.crosstab(df["W"], df["O"]).reindex(index=STATES["W"], columns=STATES["O"])
        log("Counts per (Weather, Occupancy):")
        log(ct.to_string())

    # ------------------------------------------------------------------ PART D
    section(f"PART D - LEARNING FROM DATA (MLE vs BDeu, equivalent sample size = {ESS})")
    learned = {}
    for n in SIZES:
        df = datasets[n]
        mle, unseen = learn_cpts(df, "mle")
        bde, _ = learn_cpts(df, "bdeu")
        assert verify_cpts(mle, f"MLE-{n}") and verify_cpts(bde, f"BDeu-{n}")
        learned[n] = (mle, bde)
        log(f"\n--- n = {n}: both learned networks use the expert structure; "
            f"CPTs valid. Unseen parent configs under MLE: {unseen}")
        rows = []
        ex, m, b = ac_table(cpts), ac_table(mle), ac_table(bde)
        for cfg in parent_configs("A"):
            cnt = int(((df["W"] == cfg[0]) & (df["O"] == cfg[1])).sum())
            rows.append({"Weather": cfg[0], "Occupancy": cfg[1], "N(parents)": cnt,
                         "Expert P(AC=On)": ex[cfg], "MLE": m[cfg], "BDeu": b[cfg]})
        log("Learned vs expert CPT for AC Usage, P(AC=On | Weather, Occupancy):")
        log(pd.DataFrame(rows).to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # ------------------------------------------------------------------ PART E
    section("PART E - COMPARATIVE ANALYSIS (Expert vs MLE vs Bayesian)")
    all_tables, summary = {}, []
    png_blocks = []
    for n in SIZES:
        df = datasets[n]
        mle, bde = learned[n]
        vm, vb = run_queries(mle), run_queries(bde)
        rows = []
        for i, (qid, txt, tgt, ev) in enumerate(QUERIES):
            ev_cnt = int(np.all([df[k] == v for k, v in ev.items()], axis=0).sum()) if ev else n
            rows.append({"Query": qid, "Description": txt, "Expert": expert_vals[i],
                         "MLE": vm[i], "Bayesian": vb[i],
                         "|Diff| MLE": abs(vm[i] - expert_vals[i]),
                         "|Diff| Bayesian": abs(vb[i] - expert_vals[i]),
                         "Evidence count": ev_cnt})
        t = pd.DataFrame(rows)
        all_tables[n] = t
        mm, mb = t["|Diff| MLE"].mean(), t["|Diff| Bayesian"].mean()
        summary.append((n, mm, mb))
        txt = t.to_string(index=False, float_format=lambda x: f"{x:.4f}")
        block = f"\n--- Dataset size {n} ---\n{txt}\nMean |Diff|:  MLE = {mm:.5f}   Bayesian = {mb:.5f}"
        log(block)
        png_blocks.append(block)
        t.to_csv(f"comparison_{n}.csv", index=False)

    # E.1 Mean absolute difference against dataset size
    sizes = [item[0] for item in summary]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sizes, [item[1] for item in summary], "o-", label="MLE")
    ax.plot(sizes, [item[2] for item in summary], "s-", label="Bayesian (BDeu, ESS=10)")
    ax.set_xscale("log")
    ax.set_xticks(sizes)
    ax.set_xticklabels([str(n) for n in sizes])
    ax.set_xlabel("Dataset size")
    ax.set_ylabel("Mean absolute difference over Q1-Q7")
    ax.set_title("Inference error versus dataset size")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig("mean_abs_diff_vs_size.png", dpi=150)
    plt.close(fig)

    # E.2 largest error at n=500
    t500 = all_tables[500]
    log("\nE.2  Largest error for the 500-sample dataset:")
    for col in ("|Diff| MLE", "|Diff| Bayesian"):
        i = t500[col].idxmax()
        r = t500.loc[i]
        log(f"     {col:<16s}: {r['Query']} ({r['Description']}) error {r[col]:.4f}, "
            f"evidence occurs in {int(r['Evidence count'])} of 500 samples")
    log("     Evidence counts for all queries at n=500: " +
        ", ".join(f"{r.Query}:{r['Evidence count']}" for _, r in t500.iterrows()))

    log("\nAnalysis completed.")


if __name__ == "__main__":
    main()
