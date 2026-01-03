import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class VerificationResult:
    success: bool
    log: str
    binary_path: Path
    command: List[str]


class VerificationAgent:
    """Compile the generated test case with GCC."""

    def __init__(self, gcc_binary: str = "gcc") -> None:
        self.gcc_binary = gcc_binary

    def verify(self, source_path: Path) -> VerificationResult:
        binary_path = source_path.with_suffix("")
        cmd = [
            self.gcc_binary,
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-pedantic",
            str(source_path),
            "-o",
            str(binary_path),
        ]
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        return VerificationResult(
            success=process.returncode == 0,
            log=process.stdout,
            binary_path=binary_path,
            command=cmd,
        )
