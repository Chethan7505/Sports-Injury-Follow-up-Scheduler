# AGENTS.md - rules for every AI agent in this folder

Project: Sports Injury Follow-up Scheduler (college Python mini-project, Phase 1 demo soon).
Full requirements are in PROJECT_SPEC.md. Read it before doing anything.

## HARD SYLLABUS CONSTRAINT (Unit 1 Python only)
ALLOWED imports: random, os, sys, datetime, collections
(Counter, defaultdict, OrderedDict, UserDict, UserList, UserString, deque, ChainMap, namedtuple).
ALLOWED constructs: int/float/str/bool/None, list/tuple/dict/set, functions (parameters, arguments,
return), local vs global scope, lambda, list/set/dict comprehensions, iterators (__iter__, __next__,
StopIteration), decorators, while/for/if, try/except, f-strings, and small classes ONLY for:
UserDict subclass and iterator classes.
FORBIDDEN: any other import (json, csv, itertools, functools, dataclasses, typing, enum, argparse,
time, re, pathlib, unittest, pytest), pip packages, open()/file I/O, databases, GUIs, yield/generators,
type hints, async, threads, walrus operator, match statements.

## Style
- Beginner-readable code, short functions, clear names.
- Add a one-line comment "# Unit1: <topic>" wherever a syllabus topic is demonstrated
  (helps the student explain it in a viva).

## Credit discipline (the student has a small free quota)
- Do NOT browse the web, open the browser, take screenshots or record the browser.
- Do NOT add features, files or refactors beyond the spec. Do NOT rewrite working code.
- Do NOT ask questions. Decide, and record the assumption in PROGRESS.md.
- Final reply: maximum 10 lines.
- 3-strike rule: if one bug survives 3 fix attempts, stop and report what you tried.
- Never run `python main.py` without the --demo flag (the menu is interactive and will hang).

## Handoff
After every task, append to PROGRESS.md (max 5 lines): date, what changed, what is next.
Any other agent or model must be able to resume from AGENTS.md + PROJECT_SPEC.md + PROGRESS.md.