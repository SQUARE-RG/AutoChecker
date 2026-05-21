import time
from enum import Enum
from typing import Dict, List, Literal, Optional, Set

from pydantic import BaseModel, Field, model_validator

# --- Constants ---

PROTOCOL_VERSION = 1

# --- Input Protocol (Backend -> Subprocess) ---


class TestCaseData(BaseModel):
    file_name: str
    code: str
    compliant: bool


class Language(str, Enum):
    CPP = "cpp"
    JAVA = "java"


class Framework(str, Enum):
    CLANG_TIDY = "clang-tidy"
    PMD = "pmd"
    CODEQL = "codeql"


# Configuration: Define supported languages for each framework
FRAMEWORK_SUPPORTED_LANGUAGES: Dict[Framework, Set[Language]] = {
    Framework.CLANG_TIDY: {Language.CPP},
    Framework.PMD: {Language.JAVA},
    Framework.CODEQL: {Language.CPP, Language.JAVA},
}


class GeneratorInput(BaseModel):
    protocol_version: int = PROTOCOL_VERSION

    # Configuration from CreateSessionRequest
    language: Language
    framework: Framework
    rule_name: str
    rule_description: str
    base_url: str
    model_name: str
    api_key: str

    test_cases: List[TestCaseData]

    @model_validator(mode="after")
    def check_framework_language_compatibility(self):
        allowed_languages = FRAMEWORK_SUPPORTED_LANGUAGES.get(self.framework)

        if allowed_languages is None:
            raise ValueError(f"Unknown framework configuration: {self.framework}")

        if self.language not in allowed_languages:
            supported = ", ".join(sorted(lang.value for lang in allowed_languages))
            raise ValueError(
                f"Framework '{self.framework.value}' only supports languages: {supported}. "
                f"Got: '{self.language.value}'"
            )
        return self


# --- Output Protocol (Subprocess -> Backend) ---


class MessageType(str, Enum):
    LOG = "log"
    PROGRESS = "progress"
    ARTIFACT = "artifact"
    STATUS = "status"


class GeneratorStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class BaseMessage(BaseModel):
    type: MessageType
    timestamp: float = Field(default_factory=lambda: time.time())


class LogMessage(BaseMessage):
    type: Literal[MessageType.LOG] = MessageType.LOG  # type: ignore
    level: LogLevel = LogLevel.INFO
    message: str


class ProgressMessage(BaseMessage):
    type: Literal[MessageType.PROGRESS] = MessageType.PROGRESS  # type: ignore
    stage: str  # stage description e.g. Compiling checker code


class CheckerFile(BaseModel):
    file_name: str
    content: str


class TestCaseStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    NULL = "null"


class TestCaseResult(BaseModel):
    file_name: str
    status: TestCaseStatus = TestCaseStatus.NULL


class ArtifactMessage(BaseMessage):
    type: Literal[MessageType.ARTIFACT] = MessageType.ARTIFACT  # type: ignore
    files: List[CheckerFile]
    checker_logic: Optional[str] = None
    api_knowledge: Optional[str] = None
    test_results: List[TestCaseResult] = []


class StatusMessage(BaseMessage):
    type: Literal[MessageType.STATUS] = MessageType.STATUS  # type: ignore
    status: GeneratorStatus
    error_message: Optional[str] = None
