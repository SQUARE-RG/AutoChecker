#!/usr/bin/env python3
"""Build vulnerable/fixed CodeQL database pairs for CWE-Bench-Java CVEs.

This is an experimental, resumable builder.  It prefers compiling the complete
production reactor so that CodeQL sees cross-module callers and data-flow.  The
vulnerable file paths in fix_info.csv are used for verification and only as a
fallback build scope when a complete build is not possible.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shlex
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape


IRIS_ROOT = Path(__file__).resolve().parent.parent
DATA = IRIS_ROOT / "autoql_data"
DEFAULT_CVES = IRIS_ROOT / "cves"
CODEQL = Path(os.environ.get("CODEQL_BIN", "/opt/codeql-bundle-2.23.3/codeql"))
CODEQL_SEARCH_PATH = CODEQL.parent / "qlpacks"

MAVEN_FLAGS = [
    "-B", "-V", "-e", "-U", "-DskipTests", "-DskipITs",
    "-Dfindbugs.skip", "-Dcheckstyle.skip", "-Dpmd.skip=true",
    "-Dspotbugs.skip", "-Denforcer.skip", "-Dmaven.javadoc.skip",
    "-Dlicense.skip=true", "-Drat.skip=true",
    "-Dspotless.check.skip=true", "-Djacoco.skip=true",
]

NON_PRODUCTION_MODULE_PARTS = {
    "benchmark", "benchmarks", "demo", "demos", "doc", "docbook",
    "docbooks", "docs",
    "example", "examples", "integration-test", "integration-tests",
    "it", "its", "release", "test", "tests", "testsuite",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def config_side(row: dict[str, str]) -> str:
    side = (row.get("side") or "both").strip().lower()
    if side not in {"both", "vul", "fix"}:
        raise RuntimeError(
            f"invalid side {side!r} for {row.get('project_slug')!r}; "
            "expected both, vul, or fix")
    return side


def index_side_configs(rows: list[dict[str, str]], source: str
                       ) -> dict[tuple[str, str], dict[str, str]]:
    indexed: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        slug = (row.get("project_slug") or "").strip()
        if not slug:
            continue
        key = (slug, config_side(row))
        if key in indexed:
            raise RuntimeError(f"duplicate {source} entry for {key[0]} side={key[1]}")
        indexed[key] = row
    return indexed


def side_config(indexed: dict[tuple[str, str], dict[str, str]],
                slug: str, side: str, source: str,
                required: bool = True) -> dict[str, str] | None:
    selected = indexed.get((slug, side)) or indexed.get((slug, "both"))
    if selected is None and required:
        raise RuntimeError(f"no {source} entry for {slug} side={side}")
    return selected


def maven_settings_from_environment() -> str | None:
    """Bridge HTTPS_PROXY into Maven and Maven Resolver Ant tasks."""
    settings = Path.home() / ".m2" / "settings.xml"
    if settings.is_file():
        return str(settings)
    raw_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if not raw_proxy:
        return None
    proxy = urlparse(raw_proxy)
    if not proxy.hostname or not proxy.port:
        raise RuntimeError("HTTPS_PROXY is not a valid host:port URL")
    authentication = ""
    if proxy.username:
        authentication += f"<username>{escape(proxy.username)}</username>"
    if proxy.password:
        authentication += f"<password>{escape(proxy.password)}</password>"
    content = (
        '<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 '
        'https://maven.apache.org/xsd/settings-1.0.0.xsd">'
        '<proxies><proxy><id>autoql-environment-proxy</id><active>true</active>'
        f'<protocol>{escape(proxy.scheme or "http")}</protocol>'
        f'<host>{escape(proxy.hostname)}</host><port>{proxy.port}</port>'
        f'{authentication}'
        '<nonProxyHosts>localhost|127.0.0.1</nonProxyHosts>'
        '</proxy></proxies></settings>\n'
    )
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(content, encoding="utf-8")
    settings.chmod(0o600)
    return str(settings)


def run(args: list[str], *, cwd: Path | None = None,
        env: dict[str, str] | None = None, log: Path | None = None,
        check: bool = True) -> subprocess.CompletedProcess[str]:
    display = shlex.join(args)
    print(f"+ {display}", flush=True)
    result = subprocess.run(
        args, cwd=cwd, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    if log:
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(result.stdout, encoding="utf-8")
    if result.stdout:
        lines = result.stdout.splitlines()
        # Keep batch output readable while retaining the complete per-step log.
        for line in lines[-35:]:
            print(line, flush=True)
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {display}")
    return result


def canonical_remote(value: str) -> str:
    return value.strip().rstrip("/").removesuffix(".git")


def resolve_commit(repo: Path, commit: str) -> str:
    result = run(["git", "rev-parse", f"{commit}^{{commit}}"], cwd=repo, check=False)
    if result.returncode:
        raise RuntimeError(f"commit is unavailable in {repo}: {commit}")
    return result.stdout.strip()


def validate_canonical_repo(repo_url: str, dest: Path, commits: list[str]) -> None:
    """Validate the repository prepared by get_cve_repos.py."""
    if not (dest / ".git").is_dir():
        raise RuntimeError(
            f"canonical repository is missing: {dest}; "
            "run autoql_scripts/get_cve_repos.py first")

    origin = run(["git", "remote", "get-url", "origin"], cwd=dest, check=False)
    if origin.returncode:
        raise RuntimeError(f"canonical repository has no origin remote: {dest}")
    if canonical_remote(origin.stdout) != canonical_remote(repo_url):
        raise RuntimeError(
            f"canonical repository origin mismatch at {dest}: "
            f"{origin.stdout.strip()} != {repo_url}")

    missing = []
    for commit in dict.fromkeys(commit.strip() for commit in commits if commit.strip()):
        available = run(
            ["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=dest, check=False)
        if available.returncode:
            missing.append(commit)
    if missing:
        raise RuntimeError(
            f"canonical repository is missing required commits: {', '.join(missing)}; "
            "rerun autoql_scripts/get_cve_repos.py with --force")


def latest_fix_commit(repo: Path, commits: list[str]) -> str:
    """Select the latest available fix candidate, matching AutoQL's rule."""
    candidates = [commit.strip() for commit in commits if commit.strip()]
    if not candidates:
        raise RuntimeError("no fix commit is declared in project_info.csv")
    latest: str | None = None
    latest_timestamp = 0
    for commit in candidates:
        timestamp = run(
            ["git", "show", "-s", "--format=%ct", commit],
            cwd=repo, check=False,
        )
        try:
            value = int(timestamp.stdout.strip()) if timestamp.returncode == 0 else 0
        except ValueError:
            continue
        if value > latest_timestamp:
            latest_timestamp = value
            latest = commit
    return resolve_commit(repo, latest or candidates[-1])


def prepare_source_clone(canonical: Path, repo_url: str, commit: str, dest: Path) -> str:
    """Create or safely reuse a local clone for one side of the pair."""
    expected = resolve_commit(canonical, commit)

    # Migrate the previous worktree layout only when it is safe to discard the
    # derived checkout. Tracked or untracked changes require manual review.
    if dest.exists() and (dest / ".git").is_file():
        common = run(["git", "rev-parse", "--git-common-dir"], cwd=dest)
        common_path = Path(common.stdout.strip())
        if not common_path.is_absolute():
            common_path = (dest / common_path).resolve()
        canonical_git = (canonical / ".git").resolve()
        if common_path.resolve() != canonical_git:
            raise RuntimeError(f"existing checkout is not a worktree of {canonical}: {dest}")
        status = run(["git", "status", "--porcelain"], cwd=dest)
        if status.stdout.strip():
            raise RuntimeError(f"refusing to replace modified worktree: {dest}")
        run(["git", "worktree", "remove", str(dest)], cwd=canonical)
        run(["git", "worktree", "prune"], cwd=canonical)

    if dest.exists() and (dest / ".git").is_dir():
        current = resolve_commit(dest, "HEAD")
        if current != expected:
            raise RuntimeError(
                f"existing source clone {dest} is at {current}, expected {expected}")
        print(f"Reusing source clone {dest} at {expected}")
        return expected

    if dest.exists():
        if not dest.is_dir() or any(dest.iterdir()):
            raise RuntimeError(f"non-empty non-repository destination: {dest}")
        dest.rmdir()
    dest.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "worktree", "prune"], cwd=canonical)
    run(["git", "clone", "--local", "--no-checkout", str(canonical), str(dest)])
    run(["git", "remote", "set-url", "origin", repo_url], cwd=dest)
    run(["git", "checkout", "--detach", expected], cwd=dest)
    return expected


def apply_dataset_patch(slug: str, repo: Path) -> str:
    patch = DATA / "patches" / f"{slug}.patch"
    if not patch.exists():
        return "none"
    reverse = run(["git", "apply", "--reverse", "--check", str(patch)], cwd=repo, check=False)
    if reverse.returncode == 0:
        return "already-applied"
    check = run(["git", "apply", "--check", str(patch)], cwd=repo, check=False)
    if check.returncode:
        return "not-applicable"
    run(["git", "apply", str(patch)], cwd=repo)
    return "applied"


def apply_pair_patch(slug: str, kind: str, repo: Path) -> str:
    patch = DATA / "pair-build-patches" / f"{slug}-{kind}.patch"
    if not patch.exists():
        return "none"
    reverse = run(["git", "apply", "--reverse", "--check", str(patch)], cwd=repo, check=False)
    if reverse.returncode == 0:
        return "already-applied"
    check = run(["git", "apply", "--check", str(patch)], cwd=repo, check=False)
    if check.returncode:
        raise RuntimeError(f"pair build patch does not apply: {patch}")
    run(["git", "apply", str(patch)], cwd=repo)
    return "applied"


def changed_java_files(repo: Path, bug: str, fix: str) -> list[str]:
    # When annotations are absent, use the fix commit's own diff. Comparing the
    # dataset's buggy and fixed commits can span months of unrelated changes.
    commit = run(["git", "cat-file", "-p", fix], cwd=repo).stdout
    parent_match = re.search(r"^parent ([0-9a-f]{40})$", commit, flags=re.M)
    if not parent_match:
        raise RuntimeError(f"cannot determine parent of fix commit {fix}")
    parent = parent_match.group(1)
    run(["git", "fetch", "--no-tags", "--depth", "1", "origin", parent], cwd=repo)
    result = run(["git", "diff", "--name-only", parent, fix, "--", "*.java"], cwd=repo)
    paths = [x for x in result.stdout.splitlines() if x.endswith(".java")]
    main = [x for x in paths if "/src/main/" in f"/{x}"]
    return main or paths


def nearest_maven_modules(repo: Path, files: list[str]) -> list[str]:
    modules: set[str] = set()
    for relative in files:
        current = (repo / relative).parent
        while current != repo and repo in current.parents:
            if (current / "pom.xml").exists():
                modules.add(current.relative_to(repo).as_posix())
                break
            current = current.parent
    # Remove parent modules when a more specific module was identified.
    return sorted(m for m in modules if not any(x != m and x.startswith(m + "/") for x in modules))


def internal_bom_modules(repo: Path) -> list[str]:
    """Include reactor BOMs needed by snapshot development revisions."""
    root_pom = repo / "pom.xml"
    if not root_pom.exists():
        return []
    text = root_pom.read_text(encoding="utf-8", errors="ignore")
    modules = re.findall(r"<module>\s*([^<$]+)\s*</module>", text)
    return sorted(m.strip() for m in modules if m.strip().rstrip("/").endswith("-bom"))


def reactor_modules(repo: Path) -> list[str]:
    """Return unconditional modules declared outside Maven profiles."""
    root = repo.resolve()
    seen: set[Path] = set()
    modules: set[str] = set()

    def local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    def visit(pom: Path) -> None:
        pom = pom.resolve()
        if pom in seen or not pom.is_file():
            return
        seen.add(pom)
        try:
            project = ET.parse(pom).getroot()
        except ET.ParseError:
            return
        # Only inspect a direct <modules> child. Profile modules are omitted
        # here; Maven may still activate them in the level-1 default reactor.
        module_nodes = []
        for child in project:
            if local_name(child.tag) == "modules":
                module_nodes.extend(
                    node for node in child if local_name(node.tag) == "module")
        for node in module_nodes:
            value = (node.text or "").strip().rstrip("/")
            if not value or "${" in value:
                continue
            directory = (pom.parent / value).resolve()
            try:
                relative = directory.relative_to(root).as_posix()
            except ValueError:
                continue
            modules.add(relative)
            visit(directory / "pom.xml")

    visit(root / "pom.xml")
    return sorted(modules)


def production_modules(repo: Path) -> list[str]:
    """Best-effort list of unconditional modules containing production code."""
    result = []
    for module in reactor_modules(repo):
        directory = repo / module
        if not (directory / "src" / "main" / "java").is_dir():
            continue
        pom = directory / "pom.xml"
        pom_text = pom.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"<packaging>\s*maven-plugin\s*</packaging>", pom_text):
            continue
        # Module names commonly encode their role with hyphens, for example
        # uima-docbook-tools or foo-integration-tests.  Treat those separators
        # as path boundaries too so they do not leak into the production plan.
        tokens = {
            token
            for part in Path(module).parts
            for token in re.split(r"[^a-z0-9]+", part.lower())
            if token
        }
        if tokens.isdisjoint(NON_PRODUCTION_MODULE_PARTS):
            result.append(module)
    return result


def resolve_version_files(repo: Path, files: list[str]) -> list[str]:
    """Map fix-side annotations to paths that actually exist in this revision."""
    resolved: list[str] = []
    for relative in files:
        if (repo / relative).is_file():
            resolved.append(relative)
            continue
        basename = Path(relative).name
        module = relative.split("/", 1)[0]
        candidates = [p for p in repo.rglob(basename) if "/src/main/" in p.as_posix()]
        preferred = [p for p in candidates if p.relative_to(repo).parts[0] == module]
        if len(preferred) == 1:
            resolved.append(preferred[0].relative_to(repo).as_posix())
        elif len(candidates) == 1:
            resolved.append(candidates[0].relative_to(repo).as_posix())
    return sorted(set(resolved))


def pom_required_java(repo: Path) -> int | None:
    pom = repo / "pom.xml"
    if not pom.exists():
        return None
    text = pom.read_text(encoding="utf-8", errors="ignore")
    patterns = [
        r"<maven\.compiler\.(?:target|source|release)>\s*([^<$]+)",
        r"<(?:java\.version|jdk\.version|versions\.jdk)>\s*([^<$]+)",
    ]
    found: list[int] = []
    for pattern in patterns:
        for raw in re.findall(pattern, text, flags=re.I):
            match = re.match(r"(?:1\.)?(\d+)", raw.strip())
            if match:
                found.append(int(match.group(1)))
    return max(found) if found else None


def build_environment(build: dict[str, str], repo: Path,
                      versions: dict[str, dict[str, str]],
                      allow_custom: bool = False) -> tuple[dict[str, str], str, str]:
    recorded_jdk = int(build["jdk_version"])
    detected_jdk = pom_required_java(repo)
    jdk = str(max(recorded_jdk, detected_jdk or recorded_jdk))
    java_home = versions["jdks"].get(jdk)
    if not java_home or not Path(java_home).exists():
        raise RuntimeError(f"JDK {jdk} is required but is not configured/installed")
    env = os.environ.copy()
    env["JAVA_HOME"] = java_home
    prefixes = [str(Path(java_home) / "bin"), str(CODEQL.parent)]
    tool = ""
    tool_version = ""
    if build.get("mvn_version"):
        tool, tool_version = "maven", build["mvn_version"]
        home = versions["mvn"].get(tool_version)
        if not home or not Path(home).exists():
            raise RuntimeError(f"Maven {tool_version} is required but is not configured/installed")
        prefixes.insert(0, str(Path(home) / "bin"))
    elif build.get("gradle_version"):
        tool, tool_version = "gradle", build["gradle_version"]
        home = versions["gradle"].get(tool_version)
        if build.get("use_gradlew") != "True":
            if not home or not Path(home).exists():
                raise RuntimeError(f"Gradle {tool_version} is required but is not configured/installed")
            prefixes.insert(0, str(Path(home) / "bin"))
    elif build.get("ant_version"):
        tool, tool_version = "ant", build["ant_version"]
        home = versions.get("ant", {}).get(tool_version)
        if not home or not Path(home).exists():
            raise RuntimeError(f"Ant {tool_version} is required but is not configured/installed")
        prefixes.insert(0, str(Path(home) / "bin"))
    elif allow_custom:
        tool, tool_version = "custom", "command"
        raw_proxy = env.get("HTTPS_PROXY") or env.get("https_proxy")
        proxy = urlparse(raw_proxy) if raw_proxy else None
        if proxy and proxy.hostname and proxy.port:
            proxy_options = (
                f"-Dhttp.proxyHost={proxy.hostname} -Dhttp.proxyPort={proxy.port} "
                f"-Dhttps.proxyHost={proxy.hostname} -Dhttps.proxyPort={proxy.port}"
            )
            env["ANT_OPTS"] = " ".join(
                value for value in (env.get("ANT_OPTS", ""), proxy_options) if value)
    else:
        raise RuntimeError("no supported build tool in build_info.csv")
    env["PATH"] = os.pathsep.join(prefixes + [env.get("PATH", "")])
    return env, jdk, f"{tool}-{tool_version}"


def build_plans(build: dict[str, str], repo: Path, modules: list[str],
                custom: str | None, maven_settings: str | None) -> list[dict[str, object]]:
    """Create ordered build scopes, from complete to increasingly targeted."""
    plans: list[dict[str, object]] = []
    declared = reactor_modules(repo)
    production = production_modules(repo)

    def add(level: int, scope: str, command: list[str], completeness: str,
            selected: list[str] | None = None) -> None:
        if any(plan["command"] == command for plan in plans):
            return
        plans.append({
            "level": level,
            "scope": scope,
            "command": command,
            "database_completeness": completeness,
            "declared_unconditional_modules": len(declared),
            "declared_production_modules": len(production),
            "selected_modules": selected,
        })

    if custom:
        custom_command = shlex.split(custom)
        maven_index = next(
            (index for index, arg in enumerate(custom_command)
             if Path(arg).name == "mvn"),
            None,
        )
        if (maven_settings and maven_index is not None
                and not any(arg in {"-s", "--settings"}
                            for arg in custom_command[maven_index + 1:])):
            custom_command[maven_index + 1:maven_index + 1] = [
                "-s", maven_settings,
            ]
        add(0, "dataset-custom-command", custom_command, "custom", None)

    if build.get("mvn_version"):
        compile_base = ["clean", "compile"] + MAVEN_FLAGS
        # Some reactors run copy-dependencies before compiling a downstream
        # module.  A compile-only reactor has no packaged upstream artifact in
        # that case (MDEP-187), so retry the complete scopes through package
        # before sacrificing dependency coverage with a targeted build.
        package_base = [
            "clean", "package", "-Dmaven.test.skip=true", *MAVEN_FLAGS,
        ]
        maven = ["mvn"]
        if maven_settings:
            maven += ["-s", maven_settings]
        add(1, "full-default-reactor",
            maven + compile_base, "full", production)
        add(2, "full-default-reactor-package",
            maven + package_base, "full", production)
        if production:
            selection = ["-pl", ",".join(production), "-am"]
            add(3, "explicit-production-reactor",
                maven + selection + compile_base,
                "full-production", production)
            add(4, "explicit-production-reactor-package",
                maven + selection + package_base,
                "full-production", production)
        if modules:
            add(5, "ground-truth-bidirectional-closure",
                maven + ["-pl", ",".join(modules), "-am", "-amd"] + compile_base,
                "partial", modules)
            add(6, "ground-truth-upstream-closure",
                maven + ["-pl", ",".join(modules), "-am"] + compile_base,
                "partial", modules)
    elif build.get("gradle_version"):
        wrapper = repo / "gradlew"
        gradle = "./gradlew" if wrapper.exists() else "gradle"
        add(1, "full-default-reactor",
            [gradle, "--no-daemon", "--stacktrace", "classes", "-x", "test"],
            "full", None)
        tasks = [f":{m.replace('/', ':')}:classes" for m in modules]
        if tasks:
            add(6, "ground-truth-modules",
                [gradle, "--no-daemon", "--stacktrace"] + tasks + ["-x", "test"],
                "partial", modules)
    return plans


def validate_database_metadata(db: Path, expected_sha: str) -> None:
    metadata = db / "codeql-database.yml"
    if not metadata.exists():
        raise RuntimeError(f"database metadata is missing: {metadata}")
    text = metadata.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"(?m)^finalised:\s*true\s*$", text):
        raise RuntimeError(f"database is not finalized: {db}")
    if not re.search(r"(?m)^primaryLanguage:\s*java\s*$", text):
        raise RuntimeError(f"database is not a finalized Java database: {db}")
    match = re.search(r"(?m)^\s+sha:\s*([0-9a-fA-F]{40})\s*$", text)
    actual_sha = match.group(1).lower() if match else None
    if actual_sha != expected_sha.lower():
        raise RuntimeError(
            f"database revision mismatch at {db}: "
            f"expected {expected_sha}, found {actual_sha!r}")


def database_is_final(db: Path, expected_sha: str) -> bool:
    try:
        validate_database_metadata(db, expected_sha)
    except RuntimeError:
        return False
    return True


def create_database(repo: Path, db: Path, plans: list[dict[str, object]],
                    env: dict[str, str], log_dir: Path,
                    expected_sha: str, resume: bool) -> dict[str, object]:
    if resume and database_is_final(db, expected_sha):
        print(f"Reusing finalized database {db}")
        return {
            "level": None,
            "scope": "reused-existing-database",
            "command": None,
            "database_completeness": "unknown",
            "attempts": [],
        }
    attempts: list[dict[str, object]] = []
    for plan in plans:
        command = plan["command"]
        assert isinstance(command, list)
        level = plan["level"]
        scope = plan["scope"]
        print(f"Build attempt {level}: {scope}", flush=True)
        codeql_command = [
            str(CODEQL), "database", "create", str(db),
            "--source-root", str(repo), "--language", "java", "--overwrite",
            "--command", shlex.join(command),
        ]
        log = log_dir / f"attempt-{level}-{scope}.log"
        result = run(codeql_command, cwd=repo, env=env, log=log, check=False)
        attempt = {
            "level": level,
            "scope": scope,
            "command": shlex.join(command),
            "returncode": result.returncode,
            "log": str(log),
            "compiled_reactor_projects": len(re.findall(
                r"\[INFO\][^\n]*[ \t]+SUCCESS[ \t]+\[[ \t]*\d", result.stdout)),
        }
        attempts.append(attempt)
        if result.returncode == 0:
            try:
                validate_database_metadata(db, expected_sha)
            except RuntimeError as exc:
                attempt["metadata_validation_error"] = str(exc)
                raise
            attempt["metadata_validation"] = "passed"
            selected = dict(plan)
            selected["command"] = shlex.join(command)
            selected["attempts"] = attempts
            return selected
        print(f"Attempt {level} failed; trying the next narrower scope.", flush=True)
    summary = ", ".join(
        f"level {attempt['level']}={attempt['returncode']}" for attempt in attempts)
    raise RuntimeError(f"all database build scopes failed ({summary})")


def verify_extraction(db: Path, files: list[str], work: Path) -> dict[str, list[str]]:
    targets = files[:12]
    if not targets:
        return {}
    qldir = work / "verification-query"
    qldir.mkdir(parents=True, exist_ok=True)
    (qldir / "qlpack.yml").write_text(
        'name: local/cve-pair-verification\nversion: 0.0.0\n'
        'dependencies:\n  codeql/java-all: "*"\n', encoding="utf-8")
    clauses = " or\n  ".join(
        f'p = {json.dumps(path)}' for path in targets
    )
    query = qldir / "verify.ql"
    query.write_text(
        "import java\n\npredicate target(string p) {\n  " + clauses +
        "\n}\n\nfrom RefType t, string p\nwhere p = t.getFile().getRelativePath() and target(p)\n"
        "select p, t.getQualifiedName()\n", encoding="utf-8")
    result = qldir / "result.bqrs"
    run([str(CODEQL), "query", "run", str(query), "--database", str(db),
         "--search-path", str(CODEQL_SEARCH_PATH), "--output", str(result)])
    decoded = run([str(CODEQL), "bqrs", "decode", "--format=csv", str(result)]).stdout
    rows = list(csv.reader(decoded.splitlines()))
    found: dict[str, list[str]] = {path: [] for path in targets}
    for row in rows[1:]:
        if len(row) >= 2 and row[0] in found:
            found[row[0]].append(row[1])
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cve-file", type=Path, default=DATA / "cve_pro.txt")
    parser.add_argument("--cve", action="append", dest="cves")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--root", type=Path, default=DEFAULT_CVES)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be greater than zero")

    project_rows = {r["cve_id"]: r for r in read_csv(DATA / "project_info.csv")}
    builds = index_side_configs(read_csv(DATA / "build_info.csv"), "build_info.csv")
    fixes = read_csv(DATA / "fix_info.csv")
    fix_by_slug: dict[str, list[dict[str, str]]] = {}
    for row in fixes:
        fix_by_slug.setdefault(row["project_slug"], []).append(row)
    custom_commands = index_side_configs(
        [r for r in read_csv(DATA / "build_cmds.csv") if r.get("build_cmd")],
        "build_cmds.csv",
    )
    versions = json.loads((IRIS_ROOT / "dep_configs.json").read_text())
    maven_settings = maven_settings_from_environment()
    requested = args.cves or [x.strip() for x in args.cve_file.read_text().splitlines() if x.strip()]
    if args.limit is not None:
        requested = requested[:args.limit]

    overall: list[dict[str, object]] = []
    for cve in requested:
        started = time.time()
        entry: dict[str, object] = {"cve": cve, "status": "started"}
        try:
            project = project_rows[cve]
            slug = project["project_slug"]
            vul_build = side_config(builds, slug, "vul", "build_info.csv")
            fix_build = side_config(builds, slug, "fix", "build_info.csv")
            assert vul_build is not None and fix_build is not None
            vul_custom_row = side_config(
                custom_commands, slug, "vul", "build_cmds.csv", required=False)
            fix_custom_row = side_config(
                custom_commands, slug, "fix", "build_cmds.csv", required=False)
            vul_custom = vul_custom_row["build_cmd"] if vul_custom_row else None
            fix_custom = fix_custom_row["build_cmd"] if fix_custom_row else None
            annotations = fix_by_slug.get(slug, [])
            fix_candidates = project["fix_commit_ids"].split(";")
            repo_name = project["github_repository_name"]
            cve_dir = args.root.resolve() / cve
            canonical_repo = cve_dir / repo_name
            vul_repo = cve_dir / f"{repo_name}-vul"
            fix_repo = cve_dir / f"{repo_name}-fix"
            vul_db = cve_dir / f"{cve}-vul"
            fix_db = cve_dir / f"{cve}-fix"
            logs = cve_dir / "logs"
            cve_dir.mkdir(parents=True, exist_ok=True)

            print(f"\n===== {cve}: validating canonical repository =====", flush=True)
            validate_canonical_repo(
                project["github_url"], canonical_repo,
                [project["buggy_commit_id"], *fix_candidates],
            )
            bug_commit = resolve_commit(canonical_repo, project["buggy_commit_id"])
            fix_commit = latest_fix_commit(canonical_repo, fix_candidates)

            print(f"\n===== {cve}: preparing vulnerable/fixed source clones =====", flush=True)
            bug_commit = prepare_source_clone(
                canonical_repo, project["github_url"], bug_commit, vul_repo)
            fix_commit = prepare_source_clone(
                canonical_repo, project["github_url"], fix_commit, fix_repo)
            patch_vul = apply_dataset_patch(slug, vul_repo)
            patch_fix = apply_dataset_patch(slug, fix_repo)
            pair_patch_vul = apply_pair_patch(slug, "vul", vul_repo)
            pair_patch_fix = apply_pair_patch(slug, "fix", fix_repo)

            files = sorted({x["file"] for x in annotations if x.get("file")})
            if not files:
                files = changed_java_files(fix_repo, bug_commit, fix_commit)
            vul_files = resolve_version_files(vul_repo, files)
            fix_files = resolve_version_files(fix_repo, files)
            vul_modules = sorted(set(
                nearest_maven_modules(vul_repo, vul_files) + internal_bom_modules(vul_repo)))
            fix_modules = sorted(set(
                nearest_maven_modules(fix_repo, fix_files) + internal_bom_modules(fix_repo)))
            vul_env, vul_jdk, vul_tool = build_environment(
                vul_build, vul_repo, versions, allow_custom=bool(vul_custom))
            fix_env, fix_jdk, fix_tool = build_environment(
                fix_build, fix_repo, versions, allow_custom=bool(fix_custom))
            vul_plans = build_plans(
                vul_build, vul_repo, vul_modules, vul_custom, maven_settings)
            fix_plans = build_plans(
                fix_build, fix_repo, fix_modules, fix_custom, maven_settings)
            entry.update({
                "project_slug": slug, "repository": project["github_url"],
                "canonical_repository": str(canonical_repo),
                "vul_worktree": str(vul_repo), "fix_worktree": str(fix_repo),
                "bug_commit": bug_commit, "fix_commit": fix_commit,
                "files": files,
                "vul_jdk": vul_jdk, "fix_jdk": fix_jdk,
                "vul_build_tool": vul_tool, "fix_build_tool": fix_tool,
                "vul_build_config_side": config_side(vul_build),
                "fix_build_config_side": config_side(fix_build),
                "vul_custom_command_side": (
                    config_side(vul_custom_row) if vul_custom_row else None),
                "fix_custom_command_side": (
                    config_side(fix_custom_row) if fix_custom_row else None),
                "vul_modules": vul_modules, "fix_modules": fix_modules,
                "vul_build_candidates": [
                    {**plan, "command": shlex.join(plan["command"])}
                    for plan in vul_plans
                ],
                "fix_build_candidates": [
                    {**plan, "command": shlex.join(plan["command"])}
                    for plan in fix_plans
                ],
                "patch_vul": patch_vul, "patch_fix": patch_fix,
                "pair_patch_vul": pair_patch_vul, "pair_patch_fix": pair_patch_fix,
                "vul_files": vul_files, "fix_files": fix_files,
            })

            print(f"Vulnerable plan: JDK {vul_jdk}, {vul_tool}, "
                  f"ground-truth modules={vul_modules or ['root']}, "
                  f"first scope={vul_plans[0]['scope']}")
            print(f"Fixed plan: JDK {fix_jdk}, {fix_tool}, "
                  f"ground-truth modules={fix_modules or ['root']}, "
                  f"first scope={fix_plans[0]['scope']}")
            for label, repo, db, sha, version_files, plans, env in (
                ("vul", vul_repo, vul_db, bug_commit, vul_files, vul_plans, vul_env),
                ("fix", fix_repo, fix_db, fix_commit, fix_files, fix_plans, fix_env),
            ):
                print(f"\n===== {cve}: building {label} database =====", flush=True)
                selected_build = create_database(
                    repo, db, plans, env, logs / label, sha, args.resume)
                entry[f"{label}_build"] = selected_build
                entry[f"{label}_build_scope"] = selected_build["scope"]
                entry[f"{label}_fallback_level"] = selected_build["level"]
                entry[f"{label}_database_completeness"] = selected_build[
                    "database_completeness"]
                entry[f"{label}_command"] = selected_build["command"]
                verification = verify_extraction(db, version_files, cve_dir / "verification" / label)
                entry[f"{label}_verification"] = verification
                if version_files and not any(verification.values()):
                    raise RuntimeError(f"no target types extracted from {label} database")
                entry[f"{label}_database"] = str(db)
            entry["status"] = "success"
        except Exception as exc:
            entry["status"] = "failure"
            entry["error"] = str(exc)
            print(f"ERROR {cve}: {exc}", file=sys.stderr, flush=True)
        entry["duration_seconds"] = round(time.time() - started, 2)
        overall.append(entry)
        cve_dir = args.root.resolve() / cve
        cve_dir.mkdir(parents=True, exist_ok=True)
        (cve_dir / "build-report.json").write_text(
            json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = args.root.resolve() / "cve-pair-build-report.json"
    report.write_text(json.dumps(overall, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nReport: {report}")
    print(f"Success: {sum(x['status'] == 'success' for x in overall)}/{len(overall)}")
    return 0 if all(x["status"] == "success" for x in overall) else 1


if __name__ == "__main__":
    raise SystemExit(main())
