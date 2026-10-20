# LLM Usage Log

Group TACS_G12

Every entry records: tool and model, goal, what we accepted, and what was wrong or changed and how we detected it. Nothing in this log is used as a reference for correctness: technical claims are checked against the literature (Grover 1996; Gent et al. 2017; Nielsen & Chuang, ch. 6), the course material, or by hand.

---

## Part I — N-Queens (Class B, Grover + CNF)

### Entry 1 — Project planning and `.gitignore`

| Field | Content |
|---|---|
| Tool / model | Not recorded |
| Goal | Initial project planning and generating the `.gitignore` file. |
| Accepted | The overall work breakdown and the `.gitignore`. |
| Wrong / changed | Not recorded at the time. |

### Entry 2 — Organising ideas and checking the Python files

| Field | Content |
|---|---|
| Tool / model | ChatGPT (default model) and Claude (Sonnet) |
| Goal | Organise our ideas for the Problem DSL and Solution DSL, and check that the BESSER Python files (`Metamodel_NQueens.py`, `Model_NQueens.py`, `cnf_metamodel.py`, `cnf_model.py`) were well formed and consistent with the OCL rules. |
| Accepted | Suggestions we judged correct after reading them against our own models. |
| Wrong / changed | Not recorded at the time. |

### Entry 3 — First draft of the Part I report

| Field | Content |
|---|---|
| Tool / model | Not recorded |
| Goal | Produce a first draft of the Part I report (problem, DSLs, justification of the encoding). |
| Accepted | The overall structure; the idea of modelling constraints as explicit objects and fixed positions as their own concept; the CNF-per-cell encoding with the table mapping problem concepts to clause families. |
| Wrong / incomplete | (1) The draft left several open points marked `[CONFIRM]` that the LLM could not decide for us: whether to keep `Queen`, whether to rename the literal attribute `queen`, the final encoding, and the test instances. (2) The draft itself noted that `cnf_model.py` held four unit clauses describing a full solution instead of the reduced CNF. (3) The first author initial in the Grover reference was incomplete (the author is L. K. Grover). |
| How detected | The open points were flagged in the draft itself. The reference initial was noticed while rewriting the report with Claude (Entry 4). |

### Entry 4 — Rewriting, converting and merging the report

| Field | Content |
|---|---|
| Tool / model | Claude (claude.ai), Claude Sonnet 5.5, 20 October 2026 |
| Goal | Make the report read less like generated text and explain the concepts in plain language; then convert the edited PDF to Markdown; then merge it with the existing technical `part1.md`. |
| Accepted | The plain-language explanations (CNF as a checklist, why fixed queens shrink the formula, why the "no conflicting fixed positions" rule matters), the reading of the reduced formula clause by clause, and the merged structure. We edited the text afterwards. |
| Wrong / changed | (1) The first rewrite added a Grover round count (about 2 rounds for 3 variables, 1 solution) that was not in our draft. It uses the standard formula (π/4)·√(N/M), but it is not part of the Part I deliverable and was left out of our edited version. (2) The PDF text extraction garbled the ∨ and ∧ symbols, which had to be restored when converting to Markdown. (3) Our own edited text contained "so that two of them cannot attack each other", which should read "no two of them can attack each other"; this was caught during conversion and fixed in the merged file. |
| How detected | The reduced CNF `(24) ∧ (43 ∨ 44) ∧ (¬43 ∨ ¬44) ∧ (¬24 ∨ ¬44)` and its unique solution were re-derived step by step from the cells attacked by the fixed queens (1,2) and (3,1), and match the reduction in our draft. The conversion errors were visible when comparing the PDF text with the original Markdown. |

### Entry 5 — Explaining concepts from the classes

| Field | Content |
|---|---|
| Tool / model | Gemini / NotebookLM (model not recorded) |
| Goal | Get explanations of concepts from the course material. |
| Accepted | Explanations that matched the course material. |
| Wrong / changed | Not recorded at the time. |

### Entry 6 — Creating this log file

| Field | Content |
|---|---|
| Tool / model | ChatGPT (default model) for voice input (speech-to-text), then Claude (claude.ai), Claude Sonnet 5.5, 20 October 2026, to write the log |
| Goal | Produce the LLM usage log required as a deliverable, from our own recollection of how we used LLMs. We used ai to facilitate the md formating andd creation of nice visual tables |
| Accepted | The table format (tool and model, goal, accepted, wrong, how detected) and the entries for the sessions we described. |
| Wrong / changed | (1) Claude did not invent details we had not given it: unknown models and errors were marked as not recorded rather than made up. (2) The first version of the log did not include ChatGPT or Gemini, because we had not yet told Claude about them; they were added afterwards. (3) "geminilm" in our dictated notes was ambiguous between Gemini and NotebookLM. |
