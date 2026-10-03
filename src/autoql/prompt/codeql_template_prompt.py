"""Java CodeQL prompt skeletons; {{...}} slots require model implementation.

These are generation instructions, not compilable queries. Preserve query_skeleton()
as the default taint template entry point.
"""

_COMMON = """
以 prompt 内的完整源码为依据，结合 vuln_spec.model 描述的漏洞机制，提取 API、
类型、参数位置、表达式、数据流和控制条件等可泛化特征，使用 CodeQL 语法建模，
将实现这些语义的 QL 类、谓词和约束填入对应 {{...}} 槽位。
model 是建模意图，不是可直接替换的 QL 代码；不得把字段文本机械粘贴进模板。
模板中的自定义谓词不是 CodeQL 内建 API；必须给出定义。
查询 API 不确定时调用 search_docs/get_doc_detail，使用本地 qlpack 支持的接口。
不按 evidence 的文件名、行号或 commit 硬编码告警；用 API、参数和语义约束建模。
没有证据支持的安全检查不要编造。不要保留 TODO、占位符或恒真/恒假凑数实现。
修复轮次使用 prompt 中的完整当前 query，不需要读取 query 文件。
源码不足以确定模型时返回 needs_evidence 及具体缺失信息，不猜测。
输出完整 query_code: 后的 fenced query 代码块。
"""

_HEADER = """/**
 * @name {{name}}
 * @description {{description}}
 * @kind __KIND__
 * @problem.severity warning
 * @id autoql/{{query_id}}
 */
"""

_BODIES = {
    "taint_tracking": r"""
import java
import semmle.code.java.dataflow.DataFlow
import semmle.code.java.dataflow.TaintTracking

// model.sources: match a return value, parameter, or other proven entry node.
class Source extends DataFlow::Node {
  Source() { {{model.sources}} }
}
// model.sinks: match the sensitive argument/receiver, not the call return.
class Sink extends DataFlow::Node {
  Sink() { {{model.sinks}} }
}
// Optional: remove this class and isBarrier when model.barriers is empty.
class Barrier extends DataFlow::Node {
  Barrier() { {{model.barriers}} }
}
module Config implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node n) { n instanceof Source }
  predicate isSink(DataFlow::Node n) { n instanceof Sink }
  predicate isBarrier(DataFlow::Node n) { n instanceof Barrier }
  // Optional: remove when model.additional_steps is empty.
  predicate isAdditionalFlowStep(DataFlow::Node a, DataFlow::Node b) {
    {{model.additional_steps}}
  }
}
module Flow = TaintTracking::Global<Config>;
import Flow::PathGraph

from Flow::PathNode source, Flow::PathNode sink
where Flow::flowPath(source, sink)
select sink.getNode(), source, sink, "{{message}}"
""",
    "local_data_flow": r"""
import java
import semmle.code.java.dataflow.DataFlow
import semmle.code.java.dataflow.TaintTracking

predicate isOrigin(DataFlow::Node n) { {{model.origins}} }
predicate isTarget(DataFlow::Node n) { {{model.targets}} }
predicate sameScope(DataFlow::Node a, DataFlow::Node b) {
  {{model.scope}}
}
predicate propagates(DataFlow::Node a, DataFlow::Node b) {
  {{model.flow_semantics_and_local_steps}}
}
predicate excludedPair(DataFlow::Node a, DataFlow::Node b) {
  {{model.excluded_patterns}}
}

from DataFlow::Node origin, DataFlow::Node target
where
  isOrigin(origin) and isTarget(target) and
  sameScope(origin, target) and propagates(origin, target) and
  not excludedPair(origin, target)
select target, "{{message}}"
""",
    "structural_pattern": r"""
import java

predicate candidate(Expr operation) { {{model.required_patterns}} }
predicate applicableContext(Expr operation) { {{model.context_constraints}} }
predicate safeException(Expr operation) { {{model.excluded_patterns}} }

from Expr operation
where
  candidate(operation) and applicableContext(operation) and
  not safeException(operation)
select operation, "{{message}}"
""",
    "control_flow_guard": r"""
import java
{{imports_for_verified_Java_control_flow_API}}

predicate sensitiveOperation(Expr operation) { {{model.sensitive_operations}} }
predicate protectedOperation(Expr operation) {
  exists(Expr guard |
    {{model.required_guards}} and
    {{model.subject_relation}} and
    {{model.guard_relation}} and
    {{no_invalidation_from_model.invalidation_conditions}}
  )
}

from Expr operation
where sensitiveOperation(operation) and not protectedOperation(operation)
select operation, "{{message}}"
""",
    "stateful_protocol": r"""
import java
{{imports_for_verified_CFG_and_alias_models}}

predicate initial(Expr event, Expr subject, string state) {
  {{model.initial_states_and_subject}}
}
predicate transition(
  Expr event, Expr subject, string before, string after
) { {{model.transitions}} }
predicate nextRelevant(Expr a, Expr b, Expr subject) {
  {{model.event_order_and_subject}}
}
predicate reaches(Expr event, Expr subject, string state) {
  initial(event, subject, state)
  or
  exists(Expr previous, string before |
    reaches(previous, subject, before) and
    nextRelevant(previous, event, subject) and
    transition(event, subject, before, state)
  )
}
predicate invalidUse(Expr event, Expr subject, string state) {
  {{model.invalid_sequences_or_terminal_effects}}
}

from Expr previous, Expr operation, Expr subject, string state
where
  reaches(previous, subject, state) and
  nextRelevant(previous, operation, subject) and
  invalidUse(operation, subject, state)
select operation, "{{message}}"
""",
    "configuration": r"""
import java
{{imports_for_extracted_configuration_format_if_available}}

predicate configurationAt(Expr consumer, string key, string value) {
  {{model.declarations_readers_and_propagation}}
}
predicate unsafeValue(string key, string value) { {{model.unsafe_values}} }
predicate dangerousEffect(Expr consumer) { {{model.effects}} }
predicate safeOverride(Expr consumer, string key, string value) {
  {{model.safe_values_and_precedence}}
}

from Expr consumer, string key, string value
where
  configurationAt(consumer, key, value) and
  unsafeValue(key, value) and dangerousEffect(consumer) and
  not safeOverride(consumer, key, value)
select consumer, "{{message}}"
""",

}

_GUIDANCE = {
    "taint_tracking": """
映射 model.sources/sinks/barriers/additional_steps。
source 绑定不可信返回值/参数节点；sink 绑定危险实参/receiver，而非整条调用结果。
优先使用已有库传播模型。只为证实缺失的传播增加边，不能任意连接 source 与 sink。
路径相关的条件检查不能随意写成屏蔽整个值的 isBarrier；必须验证安全分支和被检查值。
""",
    "local_data_flow": """
映射 scope/origins/targets/local_steps/excluded_patterns。
model.flow_semantics=value_preserving 使用 DataFlow::localFlow；
model.flow_semantics=taint 使用 TaintTracking::localTaint。
二者都必须限制在同一个 callable。没有 excluded_patterns 时删除 excludedPair 及引用。
需要额外边时定义有界 localStep 与闭包，并保证每条边同 scope；不能拼接任意全局边。
只有表达式转换也传播污点时，不能因为代码都在一个方法里就选择 localFlow。
""",
    "structural_pattern": """
映射 required_patterns/context_constraints/excluded_patterns/report_location。
模板以 Expr 为例；根据证据改成 Method、Field、Stmt 等实际可定位的实体类型。
没有上下文限制或排除项时删除对应谓词和调用；不要保留空谓词。
谓词表达安全语义：限定完整 API、重载、参数值和上下文；不要只匹配方法名或源码文本。
""",
    "control_flow_guard": """
映射 sensitive_operations/required_guards/subject_relation/guard_relation/invalidation_conditions。
protectedOperation 是待实现语义谓词，不是库函数。
检查必须针对同一值/资源，且满足正确分支、顺序和必要的无失效条件。
invalidation_conditions 列举失效事件；protectedOperation 必须证明这些事件未发生。
仅存在 guard 调用、源码行号在前、或条件节点 dominates 均不足以证明安全分支成立。
根据本地 Java 库检索可用控制流 API，不照抄其他语言的 guards 类。
""",
    "stateful_protocol": """
映射 subject/initial_states/transitions/event_order/invalid_sequences/terminal_effects。
string state 必须来自有限枚举，所有变量有有限绑定域。
nextRelevant 必须跟踪同一对象及其 alias，正确处理重赋值、reset、异常路径和循环。
不能使用源码行号排序代替执行顺序。存在路径结果可能是保守近似，记录分析限制。
模板覆盖非法状态下的使用；若检测退出时未释放，改成出口事件仍处于 live 状态。
跨函数问题需明确定义调用/返回与状态传递，不能以局部 CFG 假装完成全局协议分析。
""",
    "configuration": """
映射 declarations/readers/unsafe_values/safe_values/precedence/effects/propagation。
先验证配置格式是否被数据库提取；否则在代码中的配置读取/default/setter 建模。
模板报告 Java consumer。若配置 AST 可用且需要报告声明，改为对应可定位节点类型。
必须处理缺省值、配置覆盖优先级和实际消费者。不要把缺失值当成空字符串。
不能用任意文件读取假装 CodeQL 数据库拥有 YAML/JSON 模型；模型不可用则反馈 unsupported。
""",

}


_EXAMPLES = {
    "taint_tracking": """
适用例：request.getParameter("name") 经 helper 拼接成为路径，再传入 FileOutputStream。
sources=请求返回值；sinks=写文件构造器第 0 个实参；
barriers=同一规范化路径在可信目录中的有效 containment 检查（如确实存在）；
additional_steps=确认库未覆盖的 helper 传播。sink 上的操作/guard 限制直接合入 sink 谓词。
不适用：固定常量参数禁用 TLS 验证，这无需证明不可信数据传播。
Java 映射示例（API/重载应以证据为准）：
Source: exists(MethodCall call |
  call.getMethod().hasName("getParameter") and
  call.getMethod().getDeclaringType().hasQualifiedName("javax.servlet.http", "HttpServletRequest") and
  this.asExpr() = call)
Sink: exists(ConstructorCall call |
  call.getConstructedType().hasQualifiedName("java.io", "FileOutputStream") and
  this.asExpr() = call.getArgument(0))
这些只是语法示例，不能将示例 API 原样注入不相关任务；接口实现/重载需适当建模。
""",
    "local_data_flow": """
适用例：同一方法内 String x=request.getParameter("cmd"); Runtime.getRuntime().exec(x)。
scope=该 callable；origins=getParameter 返回值；targets=exec 第 0 个实参；
flow_semantics=value_preserving，propagates 使用 DataFlow::localFlow(a,b)。
若 x="sh -c "+request.getParameter("cmd")，应使用 taint / localTaint；
若链经过其他函数或字段且局部模型无法覆盖，改选 taint_tracking。
""",
    "structural_pattern": """
适用例：XMLInputFactory factory 的 SUPPORT_DTD 被设为 true，
在明确使用不可信 XML 的上下文中启用危险能力。required_patterns=目标 setter 与危险常量；
context_constraints=相关 factory/消费者语义；excluded_patterns=证明有效的后续安全覆盖；
report_location=危险调用。动态值来源才是漏洞关键时，改用配置/数据流模型。
""",
    "control_flow_guard": """
适用例：if (isAdmin(user)) audit(); deleteAccount(user);
deleteAccount 在非管理员分支仍执行。sensitive_operations=删除操作；
required_guards=isAdmin；subject_relation=校验和操作针对同一用户；
guard_relation=true 分支必须控制该操作；invalidation_conditions=身份或资源未被替换。
修复将 deleteAccount 移进 true 分支。不能只查是否存在 isAdmin 调用。
""",
    "stateful_protocol": """
适用例：敏感资源打开后，一条异常路径绕过关闭。
subject=同一资源实例；initial_states=打开时 live；transitions=close: live→closed；
event_order=CFG 路径中的同一资源事件；terminal_effects=方法出口仍 live。
exit 节点可能不是 Expr，必须据本地库改事件类型和 select 的可定位表达式。
若检测 close 后 use，invalid_sequences=closed 状态下使用，可使用当前骨架。
""",
    "configuration": """
适用例：verifyPeer = config.getBoolean("tls.verify", false) 使缺省状态禁用证书校验。
declarations=配置键；readers=getBoolean；unsafe_values=false；
safe_values=true；precedence=显式值覆盖缺省值；effects=TLS client 使用该值；
propagation=reader 到 TLS client setter。必须建模缺失配置时的有效默认值。
若数据库不提取配置文件，可分析 Java reader/default/setter；否则报告模型能力不足。
""",
}


def query_skeleton(analysis_kind: str = "taint_tracking") -> str:
    """Return instructions and a strategy-specific, deliberately incomplete QL skeleton."""
    if analysis_kind == "fallback":
        analysis_kind = "taint_tracking"
        fallback_note = (
            "\n兜底复用 taint 模板，仍须 model.sources/sinks 有真实证据；"
            "没有 source→sink 则返回 unsupported，禁止捏造。\n"
        )
    else:
        fallback_note = ""
    if analysis_kind not in _BODIES:
        raise ValueError(f"Unsupported analysis_kind: {analysis_kind}")
    kind = "path-problem" if analysis_kind in {"taint_tracking"} else "problem"
    header = _HEADER.replace("__KIND__", kind)
    return (
        _COMMON + fallback_note + "\n" + _GUIDANCE[analysis_kind] + "\n" + _EXAMPLES[analysis_kind]
        + "\n```ql\n" + header + _BODIES[analysis_kind].strip() + "\n```"
    )


def supported_analysis_kinds() -> tuple[str, ...]:
    """Names accepted by query_skeleton; unknown strategies fail explicitly."""
    return (*_BODIES, "fallback")
