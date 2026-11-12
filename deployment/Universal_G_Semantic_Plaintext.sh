#!/usr/bin/env bash
set -euo pipefail

# G7 — first-order semantic-preservation finite-model verifier.
# Plaintext Python source (no base64, zlib, eval, exec, or network operations).
python3 - "$@" <<'PYTHON_G7'
#!/usr/bin/env python3
"""G7 finite model witnesses for positive-existential preservation and isomorphism invariance.
No network, no repository reads, no code execution beyond this finite verifier.
"""
import itertools
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def model(name, domain, unary, binary):
    d = tuple(domain)
    return {"name": name, "D": d, "P": set(unary), "R": set(binary),
            "Care": set(unary), "Link": set(binary)}


models = [
    model("A", (0, 1), (0,), ((0, 1),)),
    model("B", (0, 1, 2), (0, 2), ((0, 1), (1, 1), (2, 1))),
    model("C", (0,), (0,), ((0, 0),)),
    model("A_renamed", (0, 1), (1,), ((1, 0),)),
    model("Z", (0, 1), (), ()),
]


def interpret(phi, m, env):
    op = phi[0]
    if op in ("P", "Care"):
        return env[phi[1]] in m[op]
    if op in ("R", "Link"):
        return (env[phi[1]], env[phi[2]]) in m[op]
    if op == "=":
        return env[phi[1]] == env[phi[2]]
    if op == "not":
        return not interpret(phi[1], m, env)
    if op in ("and", "or"):
        l, r = interpret(phi[1], m, env), interpret(phi[2], m, env)
        return (l and r) if op == "and" else (l or r)
    if op in ("exists", "forall"):
        truths = (interpret(phi[2], m, {**env, phi[1]: x}) for x in m["D"])
        return any(truths) if op == "exists" else all(truths)
    raise ValueError("unknown formula")


def translate(phi):
    op = phi[0]
    if op in ("P", "R"):
        return (("Care" if op == "P" else "Link"), *phi[1:])
    if op == "=":
        return phi
    if op == "not":
        return (op, translate(phi[1]))
    if op in ("and", "or"):
        return (op, translate(phi[1]), translate(phi[2]))
    if op in ("exists", "forall"):
        return (op, phi[1], translate(phi[2]))
    raise ValueError("unknown formula")


P, R, EQ = ("P", "x"), ("R", "x", "y"), ("=", "x", "y")
positive = [P, R, EQ, ("and", P, R), ("or", P, R),
            ("exists", "x", R),
            ("exists", "y", ("and", P, R)),
            ("exists", "x", ("exists", "y", ("and", P, R))),
            ("or", ("exists", "x", R), EQ)]
full = positive + [("not", P), ("not", EQ), ("forall", "y", ("or", P, R)),
                   ("not", ("exists", "x", ("and", P, R))),
                   ("forall", "x", ("exists", "y", R))]


def maps_between(a, b):
    for values in itertools.product(b["D"], repeat=len(a["D"])):
        f = dict(zip(a["D"], values))
        if all(f[x] in b["P"] for x in a["P"]) and all(
                (f[x], f[y]) in b["R"] for x, y in a["R"]):
            yield f


def isomorphism(a, b, f):
    if len(a["D"]) != len(b["D"]) or len(set(f.values())) != len(a["D"]):
        return False
    return all((x in a["P"]) == (f[x] in b["P"]) for x in a["D"]) and all(
        ((x, y) in a["R"]) == ((f[x], f[y]) in b["R"])
        for x in a["D"] for y in a["D"])


homs = hom_checks = isos = iso_checks = 0
for a in models:
    for b in models:
        for f in maps_between(a, b):
            homs += 1
            iso = isomorphism(a, b, f)
            isos += int(iso)
            for x, y in itertools.product(a["D"], repeat=2):
                env = {"x": x, "y": y}
                transformed = {var: f[value] for var, value in env.items()}
                for phi in positive:
                    left, right = interpret(phi, a, env), interpret(translate(phi), b, transformed)
                    require(not left or right, "positive-existential truth not preserved")
                    hom_checks += 1
                if iso:
                    for phi in full:
                        require(interpret(phi, a, env) == interpret(translate(phi), b, transformed),
                                "isomorphism does not preserve first-order truth")
                        iso_checks += 1

# A -> C collapses both elements into zero: preserves P and R, but not negation.
a, c = models[0], models[2]
f = {0: 0, 1: 0}
require(f in list(maps_between(a, c)), "expected homomorphism absent")
not_phi, env = ("not", P), {"x": 1, "y": 0}
require(interpret(not_phi, a, env) and not interpret(translate(not_phi), c, {"x": 0, "y": 0}),
        "non-preservation witness missing")
# Relabeling has no semantic force if the target interpretation is inconsistent.
wrong = {**c, "Care": set()}
require(interpret(P, a, {"x": 0}) and not interpret(translate(P), wrong, {"x": 0}),
        "unjustified translation unexpectedly valid")
print(json.dumps({"version": "G7", "finite_models": len(models),
                  "homomorphisms": homs, "positive_preservation_tests": hom_checks,
                  "isomorphisms": isos, "full_truth_equivalences": iso_checks,
                  "not_counterexample": "A:x=1 -> C:x=0",
                  "arbitrary_rename_counterexample": True,
                  "all_domains_proved": False, "God_identity_proved": False}, sort_keys=True))
PYTHON_G7
