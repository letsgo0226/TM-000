#!/usr/bin/env python3
"""Dolphin-Omega: deterministic, offline, research-task planning prototype.

No network, subprocess, auto-deployment, or external node calls. The purported
'Dolphin formula' is explicitly UNDEFINED and is never treated as a solver.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "dolphin_omega" / "nodes.json"
DOMAINS = (
    ("ai", "Which aspects of AI functionality and memory can be preserved and verified across versions?"),
    ("human", "Which interventions have reproducible evidence for improved human healthspan?"),
    ("cross_species", "What regeneration mechanisms are observed across species and what are their limits?"),
    ("mental", "How can memories, knowledge, and cultural artifacts be preserved without assuming personal identity survives?"),
    ("spiritual", "Which claims are philosophical, experiential, or experimentally testable?"),
    ("physical", "What physical limits constrain energy, matter, and long-term information storage?"),
)
ID = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
NODE_TYPES = {"github_registry", "local_simulator", "external_opt_in"}
CAPABILITIES = {"research_planning", "encoding_verification"}


def encode_g257(data: bytes) -> int:
    n = 1
    for byte in data:
        n = n * 257 + byte + 1
    return n


def decode_g257(n: int) -> bytes:
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("G257 code must be an integer >= 1")
    data = []
    while n > 1:
        n, digit = divmod(n, 257)
        if not 1 <= digit <= 256:
            raise ValueError("not a valid byte+1 G257 code")
        data.append(digit - 1)
    if n != 1:
        raise ValueError("not a valid G257 code")
    return bytes(reversed(data))


def load_manifest(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != 1 or not isinstance(raw.get("nodes"), list):
        raise ValueError("invalid manifest version or nodes")
    nodes, seen = [], set()
    if len(raw["nodes"]) > 32:
        raise ValueError("too many nodes")
    for node in raw["nodes"]:
        if not isinstance(node, dict):
            raise ValueError("node must be an object")
        name, kind = node.get("id"), node.get("type")
        if not isinstance(name, str) or not ID.fullmatch(name) or name in seen:
            raise ValueError("invalid or duplicate node id")
        if kind not in NODE_TYPES:
            raise ValueError("invalid node type")
        if not isinstance(node.get("enabled"), bool) or not isinstance(node.get("explicit_opt_in"), bool):
            raise ValueError("enabled and explicit_opt_in must be booleans")
        caps = node.get("capabilities")
        if not isinstance(caps, list) or any(not isinstance(c, str) or c not in CAPABILITIES for c in caps):
            raise ValueError("invalid node capabilities")
        if kind == "external_opt_in" and node["enabled"] and not node["explicit_opt_in"]:
            raise ValueError("external enabled node lacks explicit opt-in")
        seen.add(name)
        nodes.append(node)
    return nodes


def plan(question: str, nodes: list[dict]) -> dict:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be nonempty")
    raw = question.encode("utf-8")
    if len(raw) > 1024:
        raise ValueError("question exceeds 1024 UTF-8 bytes")
    code = encode_g257(raw)
    if decode_g257(code) != raw:
        raise AssertionError("encoding roundtrip failed")
    eligible = sorted(n["id"] for n in nodes if n["enabled"]
                      and "research_planning" in n["capabilities"]
                      and (n["type"] != "external_opt_in" or n["explicit_opt_in"]))
    tasks = [
        {"domain": domain, "research_question": prompt,
         "candidate_solution": None, "evidence": "NOT_EVALUATED",
         "assigned_node": eligible[i % len(eligible)] if eligible else None,
         "assignment_is_simulated": True}
        for i, (domain, prompt) in enumerate(DOMAINS)
    ]
    return {
        "system": "Dolphin-Omega", "version": "0.1-research-only",
        "question": question,
        "encoding": {"scheme": "reversible-G257-byte-plus-one", "decimal": str(code), "roundtrip_verified": True},
        "dolphin_formula": {"status": "UNDEFINED_NOT_EXECUTED", "answer_generated": False},
        "node_selection": {"eligible_node_ids": eligible, "external_execution": False, "dispatch_performed": False},
        "tasks": tasks,
        "validation": {"empirical_evidence_required": True, "ethics_review_required": True,
                       "universal_optimum_proven": False, "immortality_proven": False},
        "deployment": {"mode": "OFFLINE_DRY_RUN", "production_deployed": False,
                       "requires_separate_human_approval": True},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", required=True, help="UTF-8 question (max 1024 bytes)")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    try:
        print(json.dumps(plan(args.question, load_manifest(args.manifest)), ensure_ascii=False,
                         sort_keys=True, indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
