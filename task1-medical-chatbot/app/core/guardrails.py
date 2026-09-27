"""Safety and domain rules applied around the model's answer.

The system prompt decides what the model *may* answer. This module decides what we do
with the answer afterwards: spotting a refusal, and attaching the medical disclaimer.
"""

OUT_OF_SCOPE_MARKER = "[OUT_OF_SCOPE]"

DISCLAIMER = (
    "This is general health information, not medical advice. Please consult a "
    "qualified healthcare professional about anything that affects you personally."
)


def interpret_answer(raw: str) -> tuple[str, bool]:
    """Split the model's raw reply into (clean text, in_domain flag)."""
    text = raw.strip()
    if text.startswith(OUT_OF_SCOPE_MARKER):
        return text[len(OUT_OF_SCOPE_MARKER):].strip(), False
    return text, True


def append_disclaimer(text: str) -> str:
    """Attach the medical disclaimer to an in-domain answer."""
    return f"{text}\n\n---\n_{DISCLAIMER}_"
