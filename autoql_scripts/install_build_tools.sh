#!/usr/bin/env bash
set -euo pipefail

# Install every JDK, Maven, Gradle and Ant version referenced by
# autoql_data/build_info.csv.
# SDKMAN candidate identifiers are pinned so repeated dataset builds use the
# same toolchains. Ant 1.10.12 is the Debian package used by this dataset and
# is installed with: apt-get install -y ant ant-optional
# Run with --check to report availability without installing.

iris_script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
iris_root="$(cd -- "${iris_script_dir}/.." && pwd)"
iris_build_info="${iris_root}/autoql_data/build_info.csv"
iris_dep_config="${iris_root}/dep_configs.json"
iris_user_home="$(getent passwd "$(id -u)" | cut -d: -f6)"
iris_sdkman_dir="${SDKMAN_DIR:-${iris_user_home}/.sdkman}"
iris_sdkman_init="${iris_sdkman_dir}/bin/sdkman-init.sh"
iris_mode="install"

case "${1:-}" in
    "") ;;
    --check) iris_mode="check" ;;
    -h|--help)
        echo "Usage: $0 [--check]"
        echo "  --check  Verify SDKMAN availability and show missing tools only."
        exit 0
        ;;
    *)
        echo "Unknown argument: $1" >&2
        exit 2
        ;;
esac

if [[ ! -r "${iris_sdkman_init}" ]]; then
    echo "SDKMAN is not installed at ${iris_sdkman_dir}" >&2
    echo "Install SDKMAN first, then rerun this script." >&2
    exit 1
fi
if [[ ! -r "${iris_build_info}" ]]; then
    echo "Missing dataset file: ${iris_build_info}" >&2
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required to read build_info.csv and update dep_configs.json" >&2
    exit 1
fi

# shellcheck source=/dev/null
# SDKMAN's shell functions access optional variables without ${var:-}
# guards, so nounset must remain disabled while those functions are used.
set +u
source "${iris_sdkman_init}"

mapfile -t iris_jdk_majors < <(
    python3 - "${iris_build_info}" jdk_version <<'PY'
import csv, sys
with open(sys.argv[1], newline="") as handle:
    values = {row[sys.argv[2]].strip() for row in csv.DictReader(handle)}
print(*sorted((v for v in values if v), key=int), sep="\n")
PY
)
mapfile -t iris_maven_versions < <(
    python3 - "${iris_build_info}" mvn_version <<'PY'
import csv, sys
with open(sys.argv[1], newline="") as handle:
    values = {row[sys.argv[2]].strip() for row in csv.DictReader(handle)}
print(*sorted(v for v in values if v), sep="\n")
PY
)
mapfile -t iris_gradle_versions < <(
    python3 - "${iris_build_info}" gradle_version <<'PY'
import csv, sys
with open(sys.argv[1], newline="") as handle:
    values = {row[sys.argv[2]].strip() for row in csv.DictReader(handle)}
print(*sorted(v for v in values if v), sep="\n")
PY
)
mapfile -t iris_ant_versions < <(
    python3 - "${iris_build_info}" ant_version <<'PY'
import csv, sys
with open(sys.argv[1], newline="") as handle:
    values = {(row.get(sys.argv[2]) or "").strip() for row in csv.DictReader(handle)}
print(*sorted(v for v in values if v), sep="\n")
PY
)

jdk_candidate() {
    case "$1" in
        8)  echo "8.0.514.0+1-tem" ;;
        11) echo "11.0.33.1+1-tem" ;;
        17) echo "17.0.12.0-oracle" ;;
        21) echo "21.0.12.0-oracle" ;;
        24) echo "24.0.2.0-oracle" ;;
        *)
            echo "No pinned SDKMAN candidate for JDK major $1" >&2
            return 1
            ;;
    esac
}

iris_tmp_dir="$(mktemp -d)"
trap 'rm -rf -- "${iris_tmp_dir}"' EXIT

echo "Fetching SDKMAN candidate catalogs..."
sdk list java >"${iris_tmp_dir}/java.txt"
sdk list maven >"${iris_tmp_dir}/maven.txt"
sdk list gradle >"${iris_tmp_dir}/gradle.txt"

catalog_has_token() {
    local catalog="$1"
    local token="$2"
    awk -v wanted="${token}" '
        { for (i = 1; i <= NF; i++) if ($i == wanted) found = 1 }
        END { exit(found ? 0 : 1) }
    ' "${catalog}"
}

iris_jdk_candidates=()
for major in "${iris_jdk_majors[@]}"; do
    candidate="$(jdk_candidate "${major}")"
    iris_jdk_candidates+=("${candidate}")
    if ! catalog_has_token "${iris_tmp_dir}/java.txt" "${candidate}"; then
        echo "JDK candidate is not available from SDKMAN: ${candidate}" >&2
        exit 1
    fi
done
for version in "${iris_maven_versions[@]}"; do
    if ! catalog_has_token "${iris_tmp_dir}/maven.txt" "${version}"; then
        echo "Maven version is not available from SDKMAN: ${version}" >&2
        exit 1
    fi
done
for version in "${iris_gradle_versions[@]}"; do
    if ! catalog_has_token "${iris_tmp_dir}/gradle.txt" "${version}"; then
        echo "Gradle version is not available from SDKMAN: ${version}" >&2
        exit 1
    fi
done

echo "All versions referenced by build_info.csv are available from SDKMAN."

iris_missing=0
install_candidate() {
    local tool="$1"
    local version="$2"
    local destination="${iris_sdkman_dir}/candidates/${tool}/${version}"
    if [[ -d "${destination}" ]]; then
        echo "[installed] ${tool} ${version}"
        return
    fi
    iris_missing=$((iris_missing + 1))
    if [[ "${iris_mode}" == "check" ]]; then
        echo "[missing]   ${tool} ${version}"
        return
    fi
    echo "[installing] ${tool} ${version}"
    # Answer "no" to SDKMAN's default-version prompt. The build script selects
    # tools explicitly through JAVA_HOME and PATH for each dataset entry.
    sdk install "${tool}" "${version}" <<<"n"
}

ant_version() {
    ant -version 2>/dev/null | sed -n 's/^Apache Ant(TM) version \([^ ]*\).*/\1/p'
}

for version in "${iris_ant_versions[@]}"; do
    installed="$(ant_version || true)"
    if [[ "${installed}" == "${version}" ]]; then
        echo "[installed] ant ${version}"
        continue
    fi
    iris_missing=$((iris_missing + 1))
    if [[ "${iris_mode}" == "check" ]]; then
        echo "[missing]   ant ${version} (installed: ${installed:-none})"
        continue
    fi
    if [[ "${version}" != "1.10.12" ]]; then
        echo "No pinned Debian package installation rule for Ant ${version}" >&2
        exit 1
    fi
    echo "[installing] ant ${version} with apt-get install -y ant ant-optional"
    apt-get update
    apt-get install -y ant ant-optional
    installed="$(ant_version || true)"
    if [[ "${installed}" != "${version}" ]]; then
        echo "Expected Ant ${version}, but apt installed ${installed:-none}" >&2
        exit 1
    fi
done

for candidate in "${iris_jdk_candidates[@]}"; do
    install_candidate java "${candidate}"
done
for version in "${iris_maven_versions[@]}"; do
    install_candidate maven "${version}"
done
for version in "${iris_gradle_versions[@]}"; do
    install_candidate gradle "${version}"
done

if [[ "${iris_mode}" == "check" ]]; then
    echo "Missing installations: ${iris_missing}"
    exit 0
fi

# Preserve unrelated existing entries while synchronizing every version used by
# the dataset to its SDKMAN installation directory.
python3 - "${iris_dep_config}" "${iris_sdkman_dir}" "${iris_build_info}" <<'PY'
import csv
import json
import os
import sys
import tempfile
from pathlib import Path

config_path = Path(sys.argv[1])
sdkman_dir = Path(sys.argv[2])
build_info = Path(sys.argv[3])
jdk_candidates = {
    "8": "8.0.514.0+1-tem",
    "11": "11.0.33.1+1-tem",
    "17": "17.0.12.0-oracle",
    "21": "21.0.12.0-oracle",
    "24": "24.0.2.0-oracle",
}
with build_info.open(newline="") as handle:
    rows = list(csv.DictReader(handle))

config = json.loads(config_path.read_text()) if config_path.exists() else {}
config.setdefault("jdks", {})
config.setdefault("mvn", {})
config.setdefault("gradle", {})
config.setdefault("ant", {})
for major in sorted({row["jdk_version"].strip() for row in rows if row["jdk_version"].strip()}, key=int):
    config["jdks"][major] = str(sdkman_dir / "candidates/java" / jdk_candidates[major]) + "/"
for version in sorted({row["mvn_version"].strip() for row in rows if row["mvn_version"].strip()}):
    config["mvn"][version] = str(sdkman_dir / "candidates/maven" / version) + "/"
for version in sorted({row["gradle_version"].strip() for row in rows if row["gradle_version"].strip()}):
    config["gradle"][version] = str(sdkman_dir / "candidates/gradle" / version) + "/"
for version in sorted({(row.get("ant_version") or "").strip() for row in rows if (row.get("ant_version") or "").strip()}):
    config["ant"][version] = "/usr/share/ant/"

config_path.parent.mkdir(parents=True, exist_ok=True)
fd, temporary = tempfile.mkstemp(prefix=config_path.name + ".", dir=config_path.parent)
try:
    with os.fdopen(fd, "w") as handle:
        json.dump(config, handle, indent=4, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, config_path)
except Exception:
    try:
        os.unlink(temporary)
    except FileNotFoundError:
        pass
    raise
PY

echo "Installed all dataset toolchains and updated ${iris_dep_config}."
