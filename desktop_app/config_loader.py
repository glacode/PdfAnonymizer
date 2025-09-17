from pdfanonymizer.core import PdfAnonymizerConfig

from .config_sample import REDACT_WORDS as sample_words, HEURISTIC_RULES as sample_rules

try:
    from .config_local import (
        REDACT_WORDS as local_words,
        HEURISTIC_RULES as local_rules,
    )
except ImportError:
    local_words = None
    local_rules = {}


def build_config() -> PdfAnonymizerConfig:
    terms_to_anonymize = local_words if local_words is not None else sample_words
    heuristic_rules = {**sample_rules, **local_rules}
    return {
        "terms_to_anonymize": terms_to_anonymize,
        "replacement": "[REDACTED]",
        "anonymize_alphanumeric": heuristic_rules.get("alphanumeric_words", True),
        "anonymize_letters_special": heuristic_rules.get("letters_special_chars", True),
        "anonymize_numeric_codes": heuristic_rules.get("numeric_codes", True),
    }
