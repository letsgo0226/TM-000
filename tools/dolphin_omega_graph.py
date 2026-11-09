#!/usr/bin/env python3
"""Dolphin-Ω v0.6: OFFLINE graph of research questions and falsification triggers.

Graph and citation syntax checks are not scientific evidence, source-content
validation, experiments, causal inference, or an immortality oracle.
No network, external execution, credentials, or production deployment.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from dolphin_omega import DOMAINS, ID
from dolphin_omega_literature import (
    DEFAULT_PAPERS, DEFAULT_QUEUE, validate_bibliography, validate_review_queue,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH = ROOT / "dolphin_omega" / "research_graph.json"
DOMAIN_SET = {d for d, _ in DOMAINS}
KINDS = {"paper", "hypothesis", "proposed_check", "contrary_question"}
RELATIONS = {
    "MOTIVATES_QUESTION",
    "PROPOSED_CHECK",
    "ADDRESSES_COUNTEREVIDENCE",
    "CROSS_DOMAIN_QUESTION_ONLY",
}
REQUIRED_NODE_KEYS = {
    "paper": {"id", "kind", "domain", "paper_id"},
    "hypothesis": {"id", "kind", "domain", "statement", "predicted_observation",
                   "would_count_against", "status"},
    "proposed_check": {"id", "kind", "domain", "check_kind", "method", "evaluation_criteria",
                       "status", "observed_outcome", "human_intervention"},
    "contrary_question": {"id", "kind", "domain", "question"},
}


def require_text(s, field, limit=700):
    if not isinstance(s, str) or not s.strip() or len(s) > limit:
        raise ValueError("invalid " + field)
    return s


def validate_graph(doc, paper_doc, review_doc):
    papers = validate_bibliography(paper_doc)
    states = validate_review_queue(review_doc, papers)
    if not isinstance(doc, dict) or set(doc) != {"version", "nodes", "edges", "notice"} or doc["version"] != 1:
        raise ValueError("invalid graph envelope")
    require_text(doc["notice"], "notice", 500)
    nodes, edges = doc["nodes"], doc["edges"]
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 48:
        raise ValueError("node count out of range")
    if not isinstance(edges, list) or not 1 <= len(edges) <= 128:
        raise ValueError("edge count out of range")

    by_id = {}
    for n in nodes:
        if not isinstance(n, dict):
            raise ValueError("node must be an object")
        nid, kind = n.get("id"), n.get("kind")
        if not isinstance(nid, str) or not ID.fullmatch(nid) or nid in by_id:
            raise ValueError("invalid or duplicate node id")
        if kind not in KINDS or set(n) != REQUIRED_NODE_KEYS[kind]:
            raise ValueError("invalid node kind or unsupported fields")
        if n["domain"] not in DOMAIN_SET:
            raise ValueError("unknown domain")
        if kind == "paper":
            pid = n["paper_id"]
            if pid not in papers or papers[pid]["domain"] != n["domain"]:
                raise ValueError("paper must match a curated bibliography record")
        elif kind == "hypothesis":
            for key in ("statement", "predicted_observation", "would_count_against"):
                require_text(n[key], key)
            if n["status"] != "UNTESTED":
                raise ValueError("graph cannot mark a hypothesis verified")
        elif kind == "proposed_check":
            if n["check_kind"] != "offline_literature_appraisal":
                raise ValueError("only passive literature appraisal is allowed")
            for key in ("method", "evaluation_criteria"):
                require_text(n[key], key)
            if n["status"] != "NOT_RUN" or n["observed_outcome"] is not None:
                raise ValueError("no experiment or review result is recorded")
            if n["human_intervention"] is not False:
                raise ValueError("no human or other biological intervention allowed")
        else:
            require_text(n["question"], "contrary question")
        by_id[nid] = n

    paper_nodes = {n["paper_id"] for n in nodes if n["kind"] == "paper"}
    if paper_nodes != set(papers) or len(paper_nodes) != sum(n["kind"] == "paper" for n in nodes):
        raise ValueError("all and only curated papers must be represented exactly once")
    expected = {
        "MOTIVATES_QUESTION": ("paper", "hypothesis"),
        "PROPOSED_CHECK": ("hypothesis", "proposed_check"),
        "ADDRESSES_COUNTEREVIDENCE": ("proposed_check", "contrary_question"),
        "CROSS_DOMAIN_QUESTION_ONLY": ("hypothesis", "hypothesis"),
    }
    seen_edges, incoming, outgoing = set(), defaultdict(list), defaultdict(list)
    for e in edges:
        if not isinstance(e, dict):
            raise ValueError("edge must be an object")
        rel = e.get("relation")
        if rel not in RELATIONS:
            raise ValueError("unknown edge relation")
        keys = {"from", "to", "relation", "qualification"} if rel == "CROSS_DOMAIN_QUESTION_ONLY" else {"from", "to", "relation"}
        if set(e) != keys:
            raise ValueError("invalid or extra edge fields")
        src, dst = e["from"], e["to"]
        if not isinstance(src, str) or not isinstance(dst, str) or src not in by_id or dst not in by_id or src == dst:
            raise ValueError("dangling or self-referential edge")
        if (src, dst, rel) in seen_edges:
            raise ValueError("duplicate edge")
        seen_edges.add((src, dst, rel))
        if (by_id[src]["kind"], by_id[dst]["kind"]) != expected[rel]:
            raise ValueError("invalid evidence edge type")
        if rel == "CROSS_DOMAIN_QUESTION_ONLY":
            if by_id[src]["domain"] == by_id[dst]["domain"]:
                raise ValueError("cross-domain question must cross domains")
            require_text(e["qualification"], "cross-domain limitation")
        elif by_id[src]["domain"] != by_id[dst]["domain"]:
            raise ValueError("evidence edges cannot silently transfer across domains")
        incoming[dst].append(e)
        outgoing[src].append(e)

    # Every curated paper motivates precisely one tentative hypothesis.
    # Every hypothesis must have exactly one proposed, passive literature
    # appraisal and each appraisal one explicit contrary-evidence question.
    for n in nodes:
        nid, kind = n["id"], n["kind"]
        incoming_same = [x for x in incoming[nid] if x["relation"] != "CROSS_DOMAIN_QUESTION_ONLY"]
        outgoing_same = [x for x in outgoing[nid] if x["relation"] != "CROSS_DOMAIN_QUESTION_ONLY"]
        want_in = 0 if kind == "paper" else 1
        want_out = 0 if kind == "contrary_question" else 1
        if len(incoming_same) != want_in or len(outgoing_same) != want_out:
            raise ValueError("incomplete or ambiguously linked falsification chain")
    # No dependency cycles, including optional cross-domain question links.
    visiting, visited = set(), set()
    def visit(nid):
        if nid in visiting:
            raise ValueError("evidence graph contains a cycle")
        if nid in visited:
            return
        visiting.add(nid)
        for edge in outgoing[nid]:
            visit(edge["to"])
        visiting.remove(nid)
        visited.add(nid)
    for node_id in sorted(by_id):
        visit(node_id)
    return by_id, states


def build_report(graph_doc, paper_doc, review_doc):
    by_id, states = validate_graph(graph_doc, paper_doc, review_doc)
    counts = {kind: sum(n["kind"] == kind for n in by_id.values()) for kind in sorted(KINDS)}
    cross = [e for e in graph_doc["edges"] if e["relation"] == "CROSS_DOMAIN_QUESTION_ONLY"]
    domains = sorted({n["domain"] for n in by_id.values() if n["kind"] == "paper"})
    chains = []
    for n in sorted(by_id.values(), key=lambda n: n["id"]):
        if n["kind"] != "paper":
            continue
        hypo_id = next(e["to"] for e in graph_doc["edges"] if e["from"] == n["id"] and e["relation"] == "MOTIVATES_QUESTION")
        check_id = next(e["to"] for e in graph_doc["edges"] if e["from"] == hypo_id and e["relation"] == "PROPOSED_CHECK")
        contra_id = next(e["to"] for e in graph_doc["edges"] if e["from"] == check_id and e["relation"] == "ADDRESSES_COUNTEREVIDENCE")
        chains.append({
            "domain": n["domain"], "paper_id": n["paper_id"],
            "hypothesis_id": hypo_id, "hypothesis": by_id[hypo_id]["statement"],
            "prediction": by_id[hypo_id]["predicted_observation"],
            "would_count_against": by_id[hypo_id]["would_count_against"],
            "proposed_check_id": check_id, "appraisal_criteria": by_id[check_id]["evaluation_criteria"],
            "contrary_question": by_id[contra_id]["question"],
            "human_review_state": states[n["paper_id"]],
            "falsification_plan_structure_valid": True,
            "outcome_observed": False, "scientifically_validated": False,
        })
    return {
        "system": "Dolphin-Omega", "version": "0.6-falsifiability-graph",
        "node_counts": counts, "edge_count": len(graph_doc["edges"]),
        "research_chains": chains,
        "cross_domain_links": [
            {"from": e["from"], "to": e["to"], "relation": e["relation"],
             "qualification": e["qualification"], "evidence_transfer_verified": False}
            for e in cross
        ],
        "covered_domains": domains,
        "uncovered_domains": sorted(DOMAIN_SET - set(domains)),
        "verification": {
            "graph_structure_valid": True,
            "bibliography_live_verified": False, "full_text_reviewed": False,
            "human_review_complete": False, "tests_run": False,
            "causal_inference_verified": False, "cross_species_transfer_verified": False,
            "immortality_proven": False, "dolphin_formula_defined": False,
            "global_optimum_computed": False,
        },
        "execution": {"mode": "OFFLINE_DRY_RUN", "external_dispatch": False,
                      "production_deployed": False, "approval_granted": False},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--bibliography", type=Path, default=DEFAULT_PAPERS)
    parser.add_argument("--review-queue", type=Path, default=DEFAULT_QUEUE)
    args = parser.parse_args()
    try:
        graph = json.loads(args.graph.read_text(encoding="utf-8"))
        papers = json.loads(args.bibliography.read_text(encoding="utf-8"))
        reviews = json.loads(args.review_queue.read_text(encoding="utf-8"))
        print(json.dumps(build_report(graph, papers, reviews), sort_keys=True,
                         indent=2, ensure_ascii=False))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
