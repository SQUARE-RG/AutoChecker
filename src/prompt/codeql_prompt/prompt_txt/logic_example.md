# Example
## Example 1
/root/code_check/codeql/cpp/ql/src/Security/CWE/CWE-014/MemsetMayBeDeleted.ql


Rule Description:

The rule describes a security vulnerability where using memset or bzero to clear a buffer containing sensitive data (like passwords or keys) can be optimized away by the compiler through "dead store elimination" if the buffer is not used afterward. This optimization leaves the sensitive data exposed in memory, risking retrieval by an attacker. The rule recommends using secure alternatives like memset_s (from C11), platform-specific functions such as SecureZeroMemory, or compiler flags like -fno-builtin-memset to ensure the clearing operation is not removed.


test cese code:
```cpp
char password[MAX_PASSWORD_LENGTH];
// read and verify password
memset(password, 0, MAX_PASSWORD_LENGTH);
// CHECK-MESSAGES: violate the rule

char password[MAX_PASSWORD_LENGTH];
// read and verify password
memset_s(password, MAX_PASSWORD_LENGTH, 0, MAX_PASSWORD_LENGTH);

```

logic:

```json
[
    {
        "logic_query": [
            "1. Identify calls to memory-clearing functions by matching FunctionCall nodes whose target name is \"memset\" or \"bzero\", and explicitly exclude secure alternatives such as \"memset_s\" and platform-specific secure APIs (for example \"SecureZeroMemory\").",
            "2. For each matched call, extract the destination buffer expression (first argument) and ensure it refers to a stack or heap buffer (for example, a local variable or allocated memory) rather than a constant or global read-only region.",
            "3. Verify that the clearing value corresponds to zeroing semantics (for example, the fill argument is literal 0 or equivalent), confirming that the intent is to erase the buffer contents.",
            "4. Perform a local control-flow/data-flow check to ensure that the destination buffer is not subsequently read or used after the memset/bzero call within the same scope or basic block region, indicating that the store may be considered dead by the compiler.",
            "5. Optionally strengthen the signal by checking that the buffer has been written or used prior to the memset/bzero call (for example, via assignments or function calls), suggesting it may contain sensitive data such as passwords or keys.",
            "6. Exclude cases where compiler-guaranteed clearing APIs are used (for example memset_s) or where additional mechanisms prevent optimization (such as explicit volatile accesses, inline assembly barriers, or known secure wrappers).",
            "7. Report the remaining memset/bzero calls as potential violations, emitting a result at the call site with a message explaining that the memory clear may be optimized away and recommending secure alternatives like memset_s or platform-specific secure zeroing functions."
        ]
    }
]


```


## Example2

/root/code_check/codeql/cpp/ql/src/Security/CWE/CWE-843/TypeConfusion.ql

The rule describes a type confusion vulnerability in C/C++ where unsafe C-style casts (e.g., (MyClass*)p) allow arbitrary pointer conversions without runtime checks, leading to undefined behavior if the runtime type of the pointer is incompatible with the target type. To mitigate this, the rule recommends using dynamic_cast for safe conversions between polymorphic types, as it performs runtime checks and returns nullptr on failure. If dynamic_cast is unavailable, static_cast should be used to restrict permissible conversions, and if neither is feasible, all casts must be manually verified for safety .


```cpp
void allocate_and_draw_bad() {
  Shape* shape = new Circle;
  // ...
  // BAD: Assumes that shape is always a Square
  Square* square = static_cast<Square*>(shape);
  int length = square->getLength();
}


struct Shape {
  virtual ~Shape();

  virtual void draw() = 0;
};

struct Circle : public Shape {
  Circle();

  void draw() override {
    /* ... */
  }

  int getRadius();
};

struct Square : public Shape {
  Square();

  void draw() override {
    /* ... */
  }

  int getLength();
};



void allocate_and_draw_good() {
  Shape* shape = new Circle;
  // ...
  // GOOD: Dynamically checks if shape is a Square
  Square* square = dynamic_cast<Square*>(shape);
  if(square) {
    int length = square->getLength();
  } else {
    // handle error
  }
}

```



```json
[
  {
    "logic_query": [
      "1. Define `lastField(f)` to determine whether a field `f` is the final field in its declaring class by selecting the field with the maximum byte offset among all fields of that class.",
      "2. Define `hasCompatibleFieldAtOffset(f1, offset, c2)` to check whether class `c2` has a field at the same offset as `f1` that is layout-compatible: either the target field is a bit-field, or both fields have equal size, or `f1` is the last field and its size is less than or equal to the target field size.",
      "3. Define `prefix(c1, c2)` to model structural prefix compatibility between two non-polymorphic classes: if `c1` is a union, require existence of at least one compatible field mapping into `c2`; otherwise require that for every non–bit-field in `c1`, the corresponding offset in `c2` has a compatible field.",
      "4. Define class `UnsafeCast` to represent explicit C-style, static_cast, or reinterpret_cast operations (excluding implicit casts and dynamic_cast), whose destination type is a concrete, non–uninstantiated-template class; expose this destination as `getConvertedType()`.",
      "5. Inside `UnsafeCast`, define `compatibleWith(t)` to determine whether the cast result can be safely interpreted as type `t` using five rules: exact type match; destination is a prefix of `t`; `t` is a prefix of destination; `t` is a base-class subtype of destination; or destination is a base-class subtype of `t`.",
      "6. Define `isSourceImpl(source, type)` to recognize allocation expressions (`new` / `new[]` without placement arguments) whose allocated element type is `type`, and ensure `type` has a concrete definition not coming from an uninstantiated template.",
      "7. Configure a global dataflow (`Config`) where sources are allocations (`isSourceImpl`), sinks are the unconverted operands of `UnsafeCast`, and barriers block flow through variables or through nodes whose class type is undefined or comes from uninstantiated templates; additionally disable field-flow branching and enable diff-informed mode hooks.",
      "8. Instantiate `Flow` as `DataFlow::Global<Config>` to compute interprocedural dataflow paths from allocation sources to unsafe-cast sinks.",
      "9. Define `relevantType(sink, allocatedType)` to require that there exists at least one dataflow path from some allocation of `allocatedType` to the given sink node.",
      "10. Define `isSinkImpl(sink, allocatedType, convertedType, compatible)` to bind a sink node to its enclosing `UnsafeCast`, extract the cast destination type, and compute whether that destination is compatible with the allocated source type using `UnsafeCast.compatibleWith`.",
      "11. Enumerate all dataflow paths (`Flow::flowPath`) from a source allocation node to a sink node, binding the allocated source type (`badSourceType`) and the cast destination type (`sinkType`).",
      "12. Retain only those paths where the source is an allocation of `badSourceType`, the sink corresponds to an `UnsafeCast`, and `compatible` is false, meaning the cast destination is incompatible with the allocated type.",
      "13. Suppress reports if there exists any alternative source (`goodSourceType`) that can also flow to the same sink where the cast would be compatible, to reduce false positives from infeasible paths.",
      "14. For each remaining violating path, report the sink expression with the full source-to-sink path and emit a diagnostic stating that conversion from the allocated source type to the cast destination type is invalid."
    ]
  }
]
```