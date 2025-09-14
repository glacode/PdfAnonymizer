# Default/sample words to redact
REDACT_WORDS = [
    "John Doe",
    "Secret Company",
    "123 Main St"
]

# Heuristic-based anonymization rules
# True = enabled, False = disabled
HEURISTIC_RULES = {
    "alphanumeric_words": True,  # anonymize words with letters + digits and length >= 6
    "letters_special_chars": True,  # anonymize words with letters + special chars and length > 6
}