"""AutoChecker regulation document input-processing pipeline."""

from .document_parser import parse_document
from .rule_pipeline import extract_rules
from .test_generator import generate_rule_tests

__all__ = ["parse_document", "extract_rules", "generate_rule_tests"]
