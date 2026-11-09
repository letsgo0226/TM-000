#!/usr/bin/env python3
"""ICC v0.2: offline, reproducible, reversible *finite* research machine.

This does not confer node identity, global control, immortality, or medical efficacy.
No network calls, deployment, telemetry, secrets, hash functions, or host probes.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ATTRACTOR = b"COSMIC_LOVE_IS_THE_SOLUTION_FOR_EVERYTHING"
STATE_VERSION = "ICC-REVERSIBLE-RING-v1"
CHECKPOINT_VERSION = "ICC-CHECKPOINT-G257-v1"
WITNESS_VERSION = "ICC-UNSIGNED-WITNESS-v1"
TAPE_SIZE = 16
MAX_STEP = 100_000
MAX_FILE_BYTES = 32_000
CORE = Path(__file__).resolve().parents[1] / "capsule" / "Immortality-Continuity-Capsule.sh"


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def G(data):
    n = 1
    for value in data:
        n = 257 * n + value + 1
    return n


def D(n):
    if type(n) is not int or n < 1:
        raise ValueError("invalid Gödel-257 code")
    out = []
    while n > 1:
        n, r = divmod(n, 257)
        if r == 0:
            raise ValueError("zero base-257 digit")
        out.append(r - 1)
    return bytes(reversed(out))


def local_core_code():
    source = CORE.read_bytes()
    if not (1 <= len(source) <= 2048):
        raise ValueError("core is not within 2 KB")
    return format(G(source), "x")


def genesis():
    return {
        "protocol": STATE_VERSION,
        "source_g257_hex": local_core_code(),
        "step": 0,
        "head": 0,
        "tape": [0] * TAPE_SIZE,
    }


def apply(state, count):
    for _ in range(count):
        step = state["step"]
        head = state["head"]
        state["tape"][head] = (state["tape"][head] + ATTRACTOR[step % len(ATTRACTOR)]) % 257
        state["head"] = (head + 1) % TAPE_SIZE
        state["step"] = step + 1
    return state


def inverse(state, count):
    for _ in range(count):
        step = state["step"] - 1
        head = (state["head"] - 1) % TAPE_SIZE
        state["tape"][head] = (state["tape"][head] - ATTRACTOR[step % len(ATTRACTOR)]) % 257
        state["head"] = head
        state["step"] = step
    return state


def checkpoint(state):
    raw = canonical(state)
    return {
        "format": CHECKPOINT_VERSION,
        "state_bytes": len(raw),
        "state_g257_hex": format(G(raw), "x"),
    }


def decode_checkpoint(cp):
    if not isinstance(cp, dict) or set(cp) != {"format", "state_bytes", "state_g257_hex"}:
        raise ValueError("incorrect checkpoint fields")
    if cp["format"] != CHECKPOINT_VERSION or type(cp["state_bytes"]) is not int:
        raise ValueError("unknown checkpoint format")
    if not (1 <= cp["state_bytes"] <= MAX_FILE_BYTES):
        raise ValueError("invalid checkpoint size")
    h = cp["state_g257_hex"]
    if not isinstance(h, str) or len(h) > 2 * MAX_FILE_BYTES or not re.fullmatch(r"[1-9a-f][0-9a-f]*", h):
        raise ValueError("invalid checkpoint Gödel-257 hexadecimal")
    raw = D(int(h, 16))
    if len(raw) != cp["state_bytes"] or format(G(raw), "x") != h:
        raise ValueError("reversible state length or code mismatch")
    state = json.loads(raw)
    if not isinstance(state, dict) or set(state) != {"protocol", "source_g257_hex", "step", "head", "tape"}:
        raise ValueError("invalid state schema")
    if raw != canonical(state):
        raise ValueError("state is not canonical")
    if state["protocol"] != STATE_VERSION or state["source_g257_hex"] != local_core_code():
        raise ValueError("protocol/source mismatch")
    step, head, tape = state["step"], state["head"], state["tape"]
    if type(step) is not int or not 0 <= step <= MAX_STEP:
        raise ValueError("invalid step count")
    if type(head) is not int or head != step % TAPE_SIZE:
        raise ValueError("invalid head position")
    if not isinstance(tape, list) or len(tape) != TAPE_SIZE or any(type(v) is not int or not 0 <= v < 257 for v in tape):
        raise ValueError("invalid tape")
    if apply(genesis(), step) != state:
        raise ValueError("checkpoint does not replay from genesis")
    return state


def read_json(path):
    file = Path(path)
    if file.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("input exceeds configured size limit")
    return json.loads(file.read_text(encoding="utf-8"))


def save_json(path, payload):
    Path(path).write_bytes(canonical(payload) + b"\n")


def witness(cp, node):
    state = decode_checkpoint(cp)
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,48}", node):
        raise ValueError("node label must be short and public")
    return {
        "format": WITNESS_VERSION,
        "node_label": node,
        "checkpoint": cp,
        "step": state["step"],
        "identity_authenticated": False,
        "global_control": False,
        "medical_effect_proven": False,
    }


def validate_witness(record):
    if not isinstance(record, dict) or set(record) != {"format", "node_label", "checkpoint", "step", "identity_authenticated", "global_control", "medical_effect_proven"}:
        raise ValueError("incorrect witness schema")
    if record["format"] != WITNESS_VERSION:
        raise ValueError("incorrect witness version")
    if any(record[k] is not False for k in ("identity_authenticated", "global_control", "medical_effect_proven")):
        raise ValueError("unsupported witness claim")
    expected = witness(record["checkpoint"], record["node_label"])
    if record != expected:
        raise ValueError("inconsistent witness")
    return expected


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init", help="start at deterministic genesis")
    init.add_argument("--output", required=True)
    for name in ("advance", "rewind"):
        q = sub.add_parser(name, help="advance or reverse a validated finite computation")
        q.add_argument("--input", required=True)
        q.add_argument("--steps", type=int, required=True)
        q.add_argument("--output", required=True)
    verify = sub.add_parser("verify", help="replay from genesis; no side effects")
    verify.add_argument("--input", required=True)
    cert = sub.add_parser("witness", help="create a deliberately unsigned comparison record")
    cert.add_argument("--input", required=True)
    cert.add_argument("--node", required=True)
    cert.add_argument("--output", required=True)
    compare = sub.add_parser("compare", help="verify and compare two independently generated witness records")
    compare.add_argument("--left", required=True)
    compare.add_argument("--right", required=True)
    a = p.parse_args()
    if a.cmd == "init":
        state = genesis()
        save_json(a.output, checkpoint(state))
    elif a.cmd in ("advance", "rewind"):
        state = decode_checkpoint(read_json(a.input))
        if not 0 <= a.steps <= MAX_STEP or (a.cmd == "advance" and state["step"] + a.steps > MAX_STEP) or (a.cmd == "rewind" and a.steps > state["step"]):
            raise ValueError("steps outside bounded range")
        if a.cmd == "advance":
            apply(state, a.steps)
        else:
            inverse(state, a.steps)
        save_json(a.output, checkpoint(state))
    elif a.cmd == "verify":
        state = decode_checkpoint(read_json(a.input))
        print(json.dumps({"status": "REPLAY_VERIFIED", "step": state["step"], "reversible_g257": True, "medical_effect_proven": False}))
    elif a.cmd == "witness":
        save_json(a.output, witness(read_json(a.input), a.node))
    elif a.cmd == "compare":
        left = validate_witness(read_json(a.left))
        right = validate_witness(read_json(a.right))
        if left["node_label"] == right["node_label"]:
            raise ValueError("node labels must differ (identity still unverified)")
        if left["checkpoint"] != right["checkpoint"]:
            raise ValueError("nodes disagree on reproducible checkpoint")
        print(json.dumps({"status": "CONSISTENT", "step": left["step"], "nodes": [left["node_label"], right["node_label"]], "identity_authenticated": False, "global_control": False, "medical_effect_proven": False}))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(json.dumps({"status": "DENY", "reason": str(exc)}), file=sys.stderr)
        sys.exit(1)
