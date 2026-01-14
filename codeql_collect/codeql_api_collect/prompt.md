# 任务要求
请在collect_codeql_api.py中写代码完成任务：读取codeql/cpp/ql/lib/semmle/code/cpp目录下所有.qll文件，包括子文件夹下的qll文件，解析其中的class和predicate，输出json格式的结果文档。具体任务如下：
1. 读取每一个qll文件中独立的predicate，注意排除private predicate,收集这个predicate的注释，名称，参数和实现方式。
2. 读取每一个qll文件中的class，收集这个class内部的所有predicate，class内部的其他方法也要收集。
3. 把收集的内容按照示例json格式保存下来。
# qll文件示例
以下是qll文件中内容的实例：
```codeql
/**
 * Holds if `t` is a scalar type, according to the rules specified in
 * C++03 3.9(10):
 *
 *   Arithmetic types (3.9.1), enumeration types, pointer types, and
 *   pointer to member types (3.9.2), and cv-qualified versions of these
 *   types (3.9.3) are collectively called scalar types.
 */
predicate isScalarType03(Type t) {
  exists(Type ut | ut = t.getUnderlyingType() |
    ut instanceof ArithmeticType or
    ut instanceof Enum or
    ut instanceof FunctionPointerType or
    ut instanceof PointerToMemberType or
    ut instanceof PointerType or
    isScalarType03(ut.(SpecifiedType).getUnspecifiedType())
  )
}

/**
 * A header file with the `#pragma once` include guard.
 */
class PragmaOnceIncludeGuard extends BadIncludeGuard {
  PragmaOnceIncludeGuard() {
    exists(PreprocessorPragma p | p.getFile() = this and p.getHead() = "once")
  }

  override Element blame() {
    exists(PreprocessorPragma p | p.getFile() = this and p = result and p.getHead() = "once")
  }
}


/**
 * A C/C++ nested union. For example, the type `MyNestedUnion` in:
 * ```
 * class MyClass {
 * public:
 *   union MyNestedUnion {
 *     int i;
 *     float f;
 *   };
 * };
 * ```
 */
class NestedUnion extends Union {
  NestedUnion() { this.isMember() }

  override string getAPrimaryQlClass() { result = "NestedUnion" }

  /** Holds if this member is private. */
  predicate isPrivate() { this.hasSpecifier("private") }

  /** Holds if this member is protected. */
  predicate isProtected() { this.hasSpecifier("protected") }

  /** Holds if this member is public. */
  predicate isPublic() { this.hasSpecifier("public") }
}


```

使用tree-sitter解析qll文件，解析出其中包含的所有class和predicate，注意排除private predicate,将结果整理成如example.json的形式。

代码完成后，直接运行代码，分析问题，迭代修复。