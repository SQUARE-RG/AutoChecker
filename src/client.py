import json
import sys
from typing import List, Optional

from types import (
    PROTOCOL_VERSION,
    ArtifactMessage,
    CheckerFile,
    GeneratorInput,
    GeneratorStatus,
    LogLevel,
    LogMessage,
    ProgressMessage,
    StatusMessage,
    TestCaseResult,
)


class AutoCheckerClient:
    """
    Helper class to communicate with the AutoChecker backend via Standard I/O.
    Now fully typed using Pydantic models from backend.sdk.types.
    """

    def __init__(self):
        # We write to stdout. It is CRITICAL to flush after every write.
        self.stdout = sys.stdout
        self.stdin = sys.stdin

    def get_input(self) -> GeneratorInput:
        """
        Reads the full JSON input from stdin and parses it into a strongly-typed GeneratorInput object.
        Blocks until stdin is closed by the parent process.
        """
        try:
            input_str = self.stdin.read()
            if not input_str.strip():
                raise ValueError("Empty input received from stdin")

            data = GeneratorInput.model_validate_json(input_str)

            # Protocol Version Check
            if data.protocol_version != PROTOCOL_VERSION:
                error_msg = (
                    f"[SDK Critical] Protocol version mismatch: "
                    f"Expected {PROTOCOL_VERSION}, received {data.protocol_version}. "
                    "Aborting to prevent undefined behavior."
                )
                sys.stderr.write(error_msg + "\n")
                sys.exit(1)

            return data

        except Exception as e:
            # Writing to stderr allows the backend to capture this as a log/error
            sys.stderr.write(f"[SDK Error] Failed to parse input: {str(e)}\n")
            sys.exit(1)

    def _send_model(self, model):
        """
        Internal helper to serialize and send a Pydantic message model.
        """
        # model_dump(mode='json') converts Enums to strings, etc.
        data = model.model_dump(mode="json")
        # ensure_ascii=False allows non-ASCII characters (e.g. Chinese comments)
        self.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")
        self.stdout.flush()

    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        """
        Send a log message.
        """
        msg = LogMessage(level=level, message=message)
        self._send_model(msg)

    def report_progress(self, stage: str):
        """
        Report execution progress stage.
        """
        msg = ProgressMessage(stage=stage)
        self._send_model(msg)

    def send_artifact(
        self,
        files: List[CheckerFile],
        test_results: List[TestCaseResult],
        checker_logic: str = "",
        api_knowledge: str = "",
    ):
        """
        Send a generated artifact (code) along with validation results.
        Version is now handled automatically by the backend.
        """
        msg = ArtifactMessage(
            files=files,
            test_results=test_results,
            checker_logic=checker_logic,
            api_knowledge=api_knowledge,
        )
        self._send_model(msg)

    def send_status(self, status: GeneratorStatus, error_message: Optional[str] = None):
        """
        Final status of the job.
        """
        msg = StatusMessage(status=status, error_message=error_message)
        self._send_model(msg)
