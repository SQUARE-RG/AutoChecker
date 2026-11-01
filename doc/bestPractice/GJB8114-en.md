## Best Practices

### Case Study 1: Generating Clang-Tidy Checkers from the GJB 8114 Coding Standard

**How can a PDF coding standard be transformed into static-analysis checkers that automatically detect code violations?**

This case study uses *GJB 8114-2013, Safe Subset of C/C++ Language Programming* to demonstrate how AutoChecker transforms natural-language coding requirements into structured detection rules, automatically generates compliant and violating test cases, and ultimately produces **Clang-Tidy checkers** validated through compilation and testing.

The workflow requires no manually written Clang-Tidy checker for each rule. It automates the complete transformation from **specification document → detection rules → test cases → executable checkers**.

#### End-to-End Workflow

```text
                   GJB-8114-2013.pdf
                           │
                           ▼
                 1. PDF document parsing
                 PaddleOCR PP-StructureV3
                           │
                           ▼
                 document.md + blocks.json
                           │
                           ▼
                 2. Structured rule extraction
                 LLM chunk extraction, merging,
                 and deduplication
                           │
                           ▼
                   autochecker_rules.json
                           │
                           ▼
                 3. Positive/negative test generation
                 LLM generation + C++17 compilation
                           │
                           ▼
              test_cases/ + rules_with_tests.json
                           │
                           ▼
                 4. Rule filtering and input adaptation
                 Test completeness and naming checks
                           │
                           ▼
                  supported_rules.json
                           │
                           ▼
                 5. AutoChecker checker generation
                 Knowledge retrieval → code generation
                    → compilation → testing → repair
                           │
                           ▼
                 Clang-Tidy checkers
                 + test results + generation reports
```

The workflow consists of five steps. The first three parse the specification and prepare test data, the fourth builds the input expected by AutoChecker, and the fifth automatically generates and validates the checkers.

---

#### Step 1: Parse the PDF Specification

**Goal: Transform the natural-language rules in the PDF into a structured document that an LLM can process reliably.**

This case study uses PaddleOCR PP-StructureV3 to extract headings, body text, code examples, and tables while preserving page numbers and document hierarchy so every rule can be traced back to its source.

**1. Prepare the parsing environment**

Follow the [PaddleOCR PP-StructureV3 CPU service deployment guide](../paddleocr_service_deployment_cn.md) to install and start the local document-parsing service.

**2. Run PDF parsing**

```bash
python scripts/parse_regulation_document.py \
  --input doc/GJB-8114-2013.pdf \
  --output-dir result_input_processing/gjb8114-2013
```

The parser processes 10 pages per batch by default and saves a checkpoint for each batch. If parsing is interrupted, run the same command again to continue from the existing checkpoints.

**3. Inspect the parsed artifacts**

```text
result_input_processing/gjb8114-2013/
├── source/
│   └── GJB-8114-2013.pdf       # Copy of the original specification
├── paddleocr/
│   ├── batches/                # Batch parsing checkpoints
│   └── raw_response.json       # Raw OCR response metadata
├── document.md                 # Markdown in reading order
├── blocks.json                 # Structured headings, text, and code blocks
└── manifest.json               # Source file and parsing metadata
```

`document.md` contains specification text suitable for LLM processing, for example:

```markdown
<!-- page: 5 -->

##### 5.1.1.1 Rule R-1-1-1

Do not use macro definitions to change the meaning of keywords or fundamental types.
```

`blocks.json` stores more detailed structural information:

```json
{
  "block_id": "page-5-block-12",
  "page": 5,
  "type": "paragraph_title",
  "text": "5.1.1.1 Rule R-1-1-1",
  "bbox": [102, 140, 712, 181],
  "confidence": 0.98
}
```

**Artifacts produced by this step:** `document.md` and `blocks.json`, which provide structured input and source-tracing information for rule extraction.

#### Step 2: Extract Structured Detection Rules

**Goal: Transform natural-language provisions in the specification into structured rules that AutoChecker can consume.**

The rule-extraction script uses an LLM to analyze the specification, identify rule IDs, detection requirements, rule types, and original examples, and then merge and deduplicate rules extracted from overlapping chunks or page boundaries.

**1. Run rule extraction**

```bash
python scripts/extract_regulation_rules.py \
  --parsed-dir result_input_processing/gjb8114-2013 \
  --category ucassaat \
  2>&1 | tee result_input_processing/gjb8114-2013/phase2.log
```

**2. Inspect the extraction summary**

This case study produced the following results:

| Metric | Count |
| --- | ---: |
| Document chunks | 7 |
| Initial rule candidates | 290 |
| Rules after merging and deduplication | 204 |
| Required rules | 152 |
| Advisory rules | 52 |

The main output files are:

```text
result_input_processing/gjb8114-2013/
├── chunks/                    # Document chunks and source mappings
├── extractions/               # Per-chunk LLM extraction results
├── candidates.json            # Rule candidates before merging
├── autochecker_rules.json     # Final structured rules
└── phase2.log                 # Execution log
```

**3. Examine a structured rule**

`autochecker_rules.json` uses AutoChecker's rule format:

```json
{
  "data": {
    "ucassaat": [
      {
        "rule_id": "R-1-1-2",
        "main_title": "no-macro-alias-to-keyword-basic-type",
        "description": "Do not define other identifiers as aliases for keywords or fundamental types.",
        "rule_type": "required",
        "source_chunks": ["chunk-0001"],
        "examples": [
          {
            "type": "violation",
            "code": "#define JUDGE if\n#define int64 long"
          },
          {
            "type": "compliant",
            "code": "#define JUDGE_ZERO(i) if (0 == (i))\ntypedef long int64;"
          }
        ],
        "rule_test_path": ""
      }
    ]
  }
}
```

Field descriptions:

| Field | Purpose |
| --- | --- |
| `rule_id` | Rule identifier from the specification |
| `main_title` | Unique stable name for the rule |
| `description` | Concrete coding requirement to be checked |
| `rule_type` | Rule type, such as required or advisory |
| `source_chunks` | Source chunks used to trace the rule back to the document |
| `examples` | Compliant and violating examples extracted from the specification |
| `rule_test_path` | Test-suite directory, generated and populated in the next step |

**Artifact produced by this step:** `autochecker_rules.json`, completing the transformation from a natural-language specification into structured detection rules.

> **Resumability:** The extraction result for each chunk is stored independently under `extractions/`. Completed chunks do not require another LLM call when the command is rerun.

#### Step 3: Generate Positive and Negative Test Cases

**Goal: Generate a test suite that defines and validates the expected behavior of a checker for each rule.**

A natural-language description alone does not constrain detection behavior precisely enough. AutoChecker therefore generates positive and negative test cases that express which code patterns should trigger a diagnostic and which should be accepted.

For every supported rule, the script generates by default:

- **10 negative cases:** violating code that the checker must detect.
- **10 positive cases:** compliant code that must not produce a diagnostic.

Every generated test file undergoes basic C++17 compilation. If a file fails to compile, the system uses the compiler diagnostics to attempt an automatic repair.

**1. Generate the test cases**

Run the following command from the AutoChecker project root:

```bash
python scripts/generate_rule_tests.py \
  --rules result_input_processing/gjb8114-2013/autochecker_rules.json \
  --output-dir experiment/gjb8114-all/test_cases \
  --output-rules experiment/gjb8114-all/gjb8114_rules_with_tests.json \
  --language cpp \
  2>&1 | tee result_input_processing/gjb8114-2013/phase3.log
```

**2. Inspect generated test cases**

Consider rule `R-1-1-3`:

> Do not redefine an existing typedef name in an inner scope.

Negative case:

```cpp
typedef int mytype;

int main() {
    typedef float mytype; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
    mytype value = 1.0f;
    (void)value;
    return 0;
}
```

This example redefines `mytype` in an inner scope and violates the rule.

`CHECK-MESSAGES` specifies the expected diagnostic location and checker name. It allows the later validation stage to determine whether the generated Clang-Tidy checker correctly detects the violation.

Positive case:

```cpp
typedef int mytype;

int main() {
    mytype value = 1;
    return value;
}
```

This example complies with the rule, so the generated checker must not report a violation.

**3. Inspect the test suites and generation report**

```text
experiment/gjb8114-all/
├── test_cases/
│   ├── .checkpoints/               # Per-rule generation checkpoints
│   ├── generation_report.json      # Test generation report
│   ├── no-typedef-redefinition/
│   │   ├── negative_01.cpp
│   │   ├── ...
│   │   ├── negative_10.cpp
│   │   ├── positive_01.cpp
│   │   ├── ...
│   │   └── positive_10.cpp
│   └── ...
└── gjb8114_rules_with_tests.json   # Rules populated with test-suite paths
```

After test generation succeeds, each rule is populated with its test path and case counts:

```json
{
  "rule_id": "R-1-1-3",
  "main_title": "no-typedef-redefinition",
  "description": "Do not redefine an existing typedef name in an inner scope.",
  "rule_type": "required",
  "rule_test_path": "/root/code_check/experiment/gjb8114-all/test_cases/no-typedef-redefinition",
  "negative_case_amount": 10,
  "positive_case_amount": 10
}
```

**Test-generation validity constraints**

The system does not force the creation of test files that cannot pass basic compilation. If a rule cannot be represented in a standalone C++ file, or if the violating behavior itself necessarily causes a compilation error, the system records the reason that the rule is unsupported instead of producing an invalid test.

Such a rule may, for example, be classified as `compile_error_only`. Its `rule_test_path` remains empty, and the reason is recorded in `generation_report.json`.

> **Note:** Every negative and positive case must pass basic compilation, but successful compilation does not imply compliance with the coding standard. Compliance or violation is validated in the next step by the generated Clang-Tidy checker.

**Artifacts produced by this step:** the positive and negative test suites under `test_cases/` and `gjb8114_rules_with_tests.json`, which contains the corresponding test metadata.

#### Step 4: Prepare AutoChecker's Checker-Generation Input

**Goal: Select rules with valid test suites and adapt them to the input format expected by AutoChecker.**

Not every natural-language rule is suitable for the current automated Clang-Tidy generation workflow. The results from Step 3 therefore require filtering.

Verify the following conditions:

1. `rule_test_path` is non-empty and refers to an existing test directory.
2. The positive and negative test counts are complete, and every file passes basic compilation.
3. The rule contains the `category` field required by the Clang-Tidy generation entry point.
4. Checker names in the test files match the names that will actually be generated.

Store the adapted input in:

```text
experiment/gjb8114-all/gjb8114_clang_tidy_supported_rules.json
```

Example:

```json
{
  "data": {
    "ucassaat": [
      {
        "rule_id": "R-1-1-3",
        "main_title": "no-typedef-redefinition",
        "description": "Do not redefine an existing typedef name in an inner scope.",
        "category": "ucassaat",
        "rule_test_path": "/root/code_check/experiment/gjb8114-all/test_cases/no-typedef-redefinition",
        "negative_case_amount": 10,
        "positive_case_amount": 10
      }
    ]
  }
}
```

**Important: use one consistent checker name**

The test-generation stage writes `CHECK-MESSAGES` using `category-rule_id`, for example:

```text
[ucassaat-r-1-1-3]
```

The Clang-Tidy generation entry point names checkers using `category-main_title`, for example:

```text
[ucassaat-no-typedef-redefinition]
```

These names must be made consistent before AutoChecker is started.

One option is to update the markers in the test files to:

```text
[ucassaat-no-typedef-redefinition]
```

Another option is to normalize the checker name used during generation to `r-1-1-3`.

**The checker name in each test must match the generated checker name. Otherwise, validation may fail even when the checker reports the correct violation.**

#### Step 5: Run AutoChecker to Generate Clang-Tidy Checkers

**Goal: Automatically generate Clang-Tidy checkers that compile and satisfy the positive and negative test suites.**

After deploying the Clang-Tidy development environment and configuring the relevant paths in `src/config.json`, run:

```bash
python src/main.py \
  --platform clang-tidy \
  --rules experiment/gjb8114-all/gjb8114_clang_tidy_supported_rules.json
```

**AutoChecker performs the complete checker-development workflow:**

| Stage | AutoChecker operation |
| --- | --- |
| 1. Understand the requirement | Analyze the rule description and positive/negative cases to derive the key detection conditions |
| 2. Retrieve analysis knowledge | Retrieve AST, AST Matcher, and static-analysis API knowledge needed to implement the checker |
| 3. Generate the checker | Generate the Clang-Tidy checker header, implementation, and detection logic |
| 4. Compile and repair | Integrate the candidate checker into LLVM/Clang-Tidy, compile it, and automatically repair compilation failures |
| 5. Execute tests | Run every positive and negative case to detect false negatives and false positives |
| 6. Iterate from feedback | Adjust the detection logic based on failed tests, then rebuild and rerun the suite |
| 7. Save results | Store checker source code, test reports, metrics, and intermediate iterations |

The process continues until the checker satisfies the test requirements or reaches the configured iteration limit.

**Example generated checker**

For the `no-typedef-redefinition` rule, AutoChecker generates a corresponding Clang-Tidy checker with a structure similar to the following:

```cpp
void NoTypedefRedefinitionCheck::registerMatchers(
    MatchFinder *Finder) {
  Finder->addMatcher(
      typedefDecl().bind("typedefDecl"), this);
}

void NoTypedefRedefinitionCheck::check(
    const MatchFinder::MatchResult &Result) {

  const auto *Decl =
      Result.Nodes.getNodeAs<TypedefNameDecl>("typedefDecl");

  // Determine whether this typedef shadows a declaration with the same name
  // in an enclosing scope. AutoChecker generates the actual detection logic.

  if (Decl /* && violation condition */) {
    diag(Decl->getLocation(),
         "do not redefine an existing typedef name");
  }
}
```

This excerpt only illustrates the checker's basic structure. AutoChecker generates the actual AST matching, scope analysis, and violation-detection logic from the rule and test feedback.

**Inspect the final output**

Generated results are stored under the directory configured by `result.result_dir` in `src/config.json`. For this case study, the directory is:

```text
result_generation/clang-tidy/gjb8114_security_rules/
├── checker_generation_result.json
└── no-typedef-redefinition/
    ├── checker_generation_result.json
    ├── debug_prompt/
    ├── first_checker/
    └── final_checker/
        ├── NoTypedefRedefinitionCheck.h
        └── NoTypedefRedefinitionCheck.cpp
```

Main outputs:

| File or directory | Contents |
| --- | --- |
| `final_checker/` | Final generated checker source code |
| `first_checker/` | Initial checker and intermediate iterations |
| `debug_prompt/` | Prompts used during generation, compilation repair, and test-feedback repair |
| `checker_generation_result.json` | Generation status, test results, elapsed time, and model usage |

`checker_generation_result.json` records whether generation succeeded (`issuccess`), the test pass ratio, successful and failed cases, the failure stage, elapsed time, and LLM token usage and cost.

**How do I resume an interrupted batch?**

For a large rule set, AutoChecker can resume an interrupted run:

```bash
python src/main.py \
  --platform clang-tidy \
  --rules experiment/gjb8114-all/gjb8114_clang_tidy_supported_rules.json \
  --resume
```

To retry rules that were previously recorded as failed, use:

```bash
python src/main.py \
  --platform clang-tidy \
  --rules experiment/gjb8114-all/gjb8114_clang_tidy_supported_rules.json \
  --retry-failed
```

---

#### Final Outcome

These five steps transform a PDF coding standard that was originally intended only for human readers into executable automated checks for Clang-Tidy.

| Input | Automated processing | Final output |
| --- | --- | --- |
| GJB 8114 PDF specification | Document parsing and rule extraction | Structured rule JSON |
| Natural-language rules | LLM generation and compilation validation | Compliant and violating test suites |
| Detection rules and test suites | Knowledge retrieval, code generation, compilation, validation, and feedback-driven repair | Clang-Tidy checker source code and validation reports |

**This case study demonstrates AutoChecker's central value: developers do not need to design every AST Matcher, implement every checker class, and repeatedly debug each checker by hand. Natural-language coding standards can instead be transformed into reusable automated checks.**

The generated checkers can be integrated into the Clang-Tidy toolchain and applied to code-quality enforcement and continuous integration in real projects.
