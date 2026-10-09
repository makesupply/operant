#!/usr/bin/env python3
"""Operant Instincts — a continuous-learning loop for the discipline.

The bundle is static; a deployment's *lessons* are not. Instincts captures
behavioral patterns that proved out in real sessions, scores them by
confidence, and re-surfaces the proven ones at the next session start — so the
agent gets better at THIS user's work over time without editing the bundle.

Design (deliberately conservative — this writes to what the agent reads):
  - An instinct is one behavioral pattern: trigger -> action, with evidence.
  - Confidence rises with corroboration, decays with staleness and contradiction.
  - Only instincts at/above a threshold are injected, and only the top-K, to
    respect the session-start context budget.
  - User corrections are first-class negative evidence: they can retire an
    instinct outright.
  - Everything is inspectable plain JSON the user can read, edit, or delete.

This is a reference implementation, not a background daemon. Wire `record` to a
session-Stop step (the agent proposes candidate instincts as JSON) and `inject`
to a session-Start step (emit the block into context). Stdlib only.

Commands:
  record  --file candidates.json     ingest proposed instincts (merge + score)
  correct --trigger "..." [--retire]  log a user correction (negative evidence)
  inject  [--k 7] [--min 0.7]         emit the session-start instinct block
  list    [--all]                     show the store (proven only, or everything)
  prune                               drop expired/low-confidence instincts

Store: instincts/store.json (override with --store).
"""
import argparse
import hashlib
import json
import os
import sys

# Output is captured into an agent's context block and may carry any Unicode from
# user-authored instinct text; force UTF-8 so a Windows cp1252 console can't crash us.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DEFAULT_STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store.json")
INJECT_THRESHOLD = 0.70
INJECT_TOPK = 7
RETIRE_FLOOR = 0.15          # below this, an instinct is dropped on prune
CORROBORATION_STEP = 0.12    # confidence added per corroborating observation
CONTRADICTION_STEP = 0.30    # confidence removed per contradiction/correction
STALE_AFTER = 40             # sessions since last seen before decay applies
STALE_DECAY = 0.05           # confidence removed once stale


def _key(trigger, action):
    raw = (trigger.strip().lower() + "||" + action.strip().lower()).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]


def load(store_path):
    if not os.path.exists(store_path):
        return {"session_counter": 0, "instincts": {}}
    try:
        with open(store_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"session_counter": 0, "instincts": {}}


def save(store_path, store):
    os.makedirs(os.path.dirname(store_path), exist_ok=True)
    tmp = store_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, store_path)  # atomic


def clamp(x):
    return max(0.0, min(1.0, round(x, 3)))


def cmd_record(store, args):
    """Merge proposed instincts. Each candidate: {trigger, action, evidence?, confidence?}."""
    store["session_counter"] = store.get("session_counter", 0) + 1
    now = store["session_counter"]
    try:
        with open(args.file, "r", encoding="utf-8") as fh:
            candidates = json.load(fh)
    except Exception as e:
        print(f"could not read candidates: {e}", file=sys.stderr)
        sys.exit(1)
    if isinstance(candidates, dict):
        candidates = candidates.get("instincts", [])
    added, reinforced = 0, 0
    for c in candidates:
        trig, act = c.get("trigger", "").strip(), c.get("action", "").strip()
        if not trig or not act:
            continue
        k = _key(trig, act)
        inst = store["instincts"].get(k)
        seed = clamp(c.get("confidence", 0.4))
        if inst:
            inst["confidence"] = clamp(inst["confidence"] + CORROBORATION_STEP)
            inst["observations"] += 1
            inst["last_seen"] = now
            if c.get("evidence"):
                inst["evidence"] = (inst.get("evidence", []) + [c["evidence"]])[-5:]
            reinforced += 1
        else:
            store["instincts"][k] = {
                "trigger": trig, "action": act,
                "confidence": seed, "observations": 1,
                "first_seen": now, "last_seen": now,
                "evidence": [c["evidence"]] if c.get("evidence") else [],
                "status": "candidate",
            }
            added += 1
    print(f"recorded session {now}: +{added} new, {reinforced} reinforced")


def cmd_correct(store, args):
    """A user correction is strong negative evidence against matching instincts."""
    needle = args.trigger.strip().lower()
    hit = 0
    for inst in store["instincts"].values():
        if needle in inst["trigger"].lower() or needle in inst["action"].lower():
            if args.retire:
                inst["confidence"] = 0.0
                inst["status"] = "retired"
            else:
                inst["confidence"] = clamp(inst["confidence"] - CONTRADICTION_STEP)
            inst["last_correction"] = store.get("session_counter", 0)
            hit += 1
    print(f"applied correction to {hit} instinct(s)"
          + (" (retired)" if args.retire else ""))


def _decayed(inst, now):
    c = inst["confidence"]
    if now - inst.get("last_seen", now) > STALE_AFTER:
        c = clamp(c - STALE_DECAY)
    return c


def cmd_inject(store, args):
    now = store.get("session_counter", 0)
    proven = []
    for inst in store["instincts"].values():
        if inst.get("status") == "retired":
            continue
        c = _decayed(inst, now)
        if c >= args.min:
            proven.append((c, inst))
    proven.sort(key=lambda t: -t[0])
    proven = proven[: args.k]
    if not proven:
        return  # silent: nothing proven yet
    print("## Learned instincts (from prior sessions with this user)")
    print("_Proven behavioral patterns; apply when the trigger matches. "
          "Not overrides — the discipline and the user's live instructions still win._\n")
    for c, inst in proven:
        print(f"- **When** {inst['trigger']} -> {inst['action']}  "
              f"_(confidence {c:.2f}, seen {inst['observations']}x)_")


def cmd_list(store, args):
    now = store.get("session_counter", 0)
    rows = sorted(store["instincts"].values(),
                  key=lambda i: -_decayed(i, now))
    for inst in rows:
        c = _decayed(inst, now)
        if not args.all and (c < INJECT_THRESHOLD or inst.get("status") == "retired"):
            continue
        flag = "" if inst.get("status") != "retired" else " [retired]"
        print(f"{c:.2f}  ({inst['observations']}x){flag}  {inst['trigger']} -> {inst['action']}")


def cmd_prune(store, args):
    now = store.get("session_counter", 0)
    before = len(store["instincts"])
    kept = {}
    for k, inst in store["instincts"].items():
        c = _decayed(inst, now)
        if inst.get("status") == "retired" or c < RETIRE_FLOOR:
            continue
        inst["confidence"] = c
        if c >= INJECT_THRESHOLD:
            inst["status"] = "proven"
        kept[k] = inst
    store["instincts"] = kept
    print(f"pruned {before - len(kept)} instinct(s); {len(kept)} remain")


def main():
    ap = argparse.ArgumentParser(description="Operant Instincts — continuous-learning loop")
    ap.add_argument("--store", default=DEFAULT_STORE)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("record"); p.add_argument("--file", required=True)
    p = sub.add_parser("correct"); p.add_argument("--trigger", required=True); p.add_argument("--retire", action="store_true")
    p = sub.add_parser("inject"); p.add_argument("--k", type=int, default=INJECT_TOPK); p.add_argument("--min", type=float, default=INJECT_THRESHOLD)
    p = sub.add_parser("list"); p.add_argument("--all", action="store_true")
    sub.add_parser("prune")
    args = ap.parse_args()

    store = load(args.store)
    {"record": cmd_record, "correct": cmd_correct, "inject": cmd_inject,
     "list": cmd_list, "prune": cmd_prune}[args.cmd](store, args)
    if args.cmd in ("record", "correct", "prune"):
        save(args.store, store)


if __name__ == "__main__":
    main()
