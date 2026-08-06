# Semgrep Rule Library

This directory is the formal reusable checker library. It contains accepted LLM-generated `final_rule.yml` outputs, retained prior accepted outputs after real-project noise review, and imported upstream Semgrep C checkers kept in a separate source folder.

Collection policy:

- Include accepted LLM-generated final_rule.yml outputs with paired BAD/GOOD samples.
- Include existing accepted checkers not removed by real-project noise review.
- Include imported upstream Semgrep C checkers under rules/c/semgrep_original as active non-LLM rules.
- Exclude rules removed for excessive real-project false positives.
- Exclude manual-only rules.
- Exclude failed generations.
- Exclude skipped overbroad or invalid generated rules.
- Exclude demo intermediate generated_rule.yml files.
- Exclude repair_candidate.yml and other repair artifacts.

Layout: `rules/<language>/<source>/<checker>.yml`.

| Language | Files |
|---|---:|
| `c` | 105 |
| `java` | 42 |
| `javascript` | 4 |
| `python` | 41 |
| `rust` | 9 |

| Source | Files |
|---|---:|
| `generated_20260519` | 7 |
| `generated_20260520` | 6 |
| `generated_20260524` | 67 |
| `generated_20260525` | 25 |
| `generated_20260526` | 15 |
| `generated_20260526_semgrep_migration` | 10 |
| `generated_20260527` | 1 |
| `generated_20260601` | 13 |
| `generated_20260609` | 15 |
| `generated_20260611` | 8 |
| `juliet` | 4 |
| `latest_real_project_scan` | 14 |
| `semgrep_original` | 16 |

| Logical checker groups | Count |
|---|---:|
| `checkers` | 201 |

2026-06-09 Java/Python CWE gap update: added 7 accepted Java and 8 accepted Python LLM-generated checkers under `generated_20260609`, bringing Java to 37 and Python to 38 active rules.

2026-06-11 Java/Python CWE gap round 2: added 5 accepted Java and 3 accepted Python LLM-generated checkers under `generated_20260611`, bringing Java to 42 and Python to 41 active rules. Skipped broad or low-recall candidates are recorded in `reports/20260611/java_python_cwe_expand_round2/rule_generation_review.md`.
