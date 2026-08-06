# Semgrep Rule Library

This is the formal reusable checker library for the `v1` workflow. Rules are
stored by Semgrep language and provenance:

```text
rules/
  <language>/
    <source>/
      <checker>.yml
```

The collection policy is deliberately narrow:

- keep accepted Juliet final checkers from the configured `v1` batch;
- keep final checkers selected from the latest real-project scan;
- preserve source and checker metadata in each rule;
- exclude invalid YAML, failed generations, intermediate generation files,
  repair candidates, and manually rejected rules.

`manifest.json` records the source inputs, collection time, counts, and output
paths for the current library. Rebuild the library with:

```bash
/home/meiosis/py310/bin/python \
  /home/meiosis/data/work/autochecker/code_check/semgrep_prompt/v1/collect_rule_library.py \
  --clean
```

Before a checker is added, review its paired-sample behavior and rule shape.
The library is a set of reusable alerts, not an assertion that every finding
in an arbitrary project is a vulnerability. Project results require manual
confirmation and rule-specific triage.

Scan a project directly with the language directory that applies:

```bash
semgrep scan \
  --config semgrep_prompt/rules/python \
  --config semgrep_prompt/rules/javascript \
  /path/to/project
```

The generated YAML remains a single Semgrep rule. A rule should be retained
only when its semantic intent, parseability, practical coverage, and false
positive behavior have been reviewed.
