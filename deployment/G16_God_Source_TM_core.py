#!/usr/bin/env python3
"""G16: bounded deterministic single-tape TM simulator + TM-015 prime Gödel codec.

Strictly offline, synthetic-input-only, no shell/network/market/order actions.
A bounded interpreter simulates TM steps; it is NOT a halting oracle or God.
"""
import json
import sys


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def primes256():
    out = []
    x = 2
    while len(out) < 256:
        if all(x % p for p in out if p * p <= x):
            out.append(x)
        x += 1
    return out


PRIMES = primes256()
BY_PRIME = {p: n for n, p in enumerate(PRIMES)}


def encode(data: bytes) -> int:
    n = 1
    for b in data:
        n = n * 2048 + PRIMES[b]
    return n


def decode(n: int) -> bytes:
    require(type(n) is int and n >= 1, "invalid Gödel integer")
    out = []
    while n > 1:
        n, digit = divmod(n, 2048)
        require(digit in BY_PRIME, "invalid prime digit")
        out.append(BY_PRIME[digit])
    return bytes(reversed(out))


def run(request: dict) -> dict:
    require(type(request) is dict, "request must be a JSON object")
    require(request.get("source") == "SYNTHETIC" and request.get("mode") == "paper",
            "synthetic paper only")
    for flag in ("network", "order_submission", "live_armed", "execute_external"):
        require(request.get(flag) is False, "forbidden capability: " + flag)
    steps = request.get("max_steps")
    require(type(steps) is int and 1 <= steps <= 512, "step budget 1..512")
    machine = request.get("machine")
    require(type(machine) is dict and set(machine) == {"alphabet", "blank", "start", "halt", "rules", "input"},
            "invalid machine specification")
    alphabet = machine["alphabet"]
    require(type(alphabet) is list and 1 <= len(alphabet) <= 16 and
            all(type(a) is str and 1 <= len(a) <= 12 for a in alphabet) and
            len(set(alphabet)) == len(alphabet), "invalid finite alphabet")
    blank = machine["blank"]
    start, halt = machine["start"], machine["halt"]
    require(blank in alphabet and type(start) is str and type(halt) is str and
            1 <= len(start) <= 32 and 1 <= len(halt) <= 32 and start != halt,
            "invalid start, halt, or blank")
    word = machine["input"]
    require(type(word) is list and len(word) <= 64 and all(x in alphabet for x in word),
            "input must be finite alphabet symbols")
    raw_rules = machine["rules"]
    require(type(raw_rules) is list and 1 <= len(raw_rules) <= 128, "invalid finite rule set")
    rules = {}
    for r in raw_rules:
        require(type(r) is list and len(r) == 5, "rule must be [state, read, write, move, next]")
        q, symbol, write, move, next_state = r
        require(type(q) is str and 1 <= len(q) <= 32 and q != halt and
                type(next_state) is str and 1 <= len(next_state) <= 32 and
                symbol in alphabet and write in alphabet and move in ("L", "R", "S"),
                "invalid transition")
        require((q, symbol) not in rules, "nondeterministic duplicate rule")
        rules[q, symbol] = (write, move, next_state)
    require(start in {k[0] for k in rules}, "start has no transition rule")
    # JSON emits a stable, semantically complete machine description. Not a code execution path.
    descriptor = json.dumps(machine, ensure_ascii=False, sort_keys=True,
                            separators=(",", ":")).encode("utf-8")
    require(len(descriptor) <= 8192, "descriptor size limit")
    code = encode(descriptor)
    require(decode(code) == descriptor and encode(b"") == 1 and decode(1) == b"",
            "reversible Gödel check")
    tape = {i: v for i, v in enumerate(word) if v != blank}
    head, state, count = 0, start, 0
    while count < steps and state != halt:
        key = state, tape.get(head, blank)
        if key not in rules:
            break
        write, direction, next_state = rules[key]
        if write == blank:
            tape.pop(head, None)
        else:
            tape[head] = write
        head += (direction == "R") - (direction == "L")
        state = next_state
        count += 1
        require(abs(head) <= 1024 and len(tape) <= 1024, "tape resource budget")
    status = "HALTED" if state == halt else ("STUCK" if (state, tape.get(head, blank)) not in rules else "STEP_LIMIT")
    return dict(version="G16", status=status, state=state, steps=count, head=head,
                nonblank_cells=sorted([[i, v] for i, v in tape.items()]),
                godel_roundtrip=True, godel_identity=1, descriptor_bytes=len(descriptor),
                descriptor_godel_digits=len(str(code)), orders_submitted=0,
                live_allowed=False, halting_oracle=False, god_identity_proved=False,
                certified_as_real_trading=False)


def example():
    return dict(source="SYNTHETIC", mode="paper", network=False,
                order_submission=False, live_armed=False, execute_external=False,
                max_steps=8, machine=dict(alphabet=["_", "1"], blank="_", start="scan",
                 halt="HALT", input=["1", "1"], rules=[
                    ["scan", "1", "1", "R", "scan"],
                    ["scan", "_", "1", "S", "HALT"]]))


def main():
    try:
        request = json.load(sys.stdin)
        print(json.dumps(run(request), ensure_ascii=False, sort_keys=True))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError, OverflowError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
