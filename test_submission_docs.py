"""Guard the submission scorecard and trial bank against accidental drift."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "docs" / "TRIAL_QUESTION_BANK.md"
METRICS = ROOT / "docs" / "SUBMISSION_SUCCESS_METRICS.md"


def _questions() -> list[tuple[str, str]]:
    return re.findall(
        r"^- \*\*Q(\d{3}) — [^·]+ · [^·]+ · [^*]+\.\*\* (.+)$",
        BANK.read_text(),
        re.MULTILINE,
    )


def test_trial_bank_has_160_sequential_unique_questions():
    questions = _questions()
    assert [number for number, _ in questions] == [f"{n:03d}" for n in range(1, 161)]
    normalized = [re.sub(r"\W+", " ", text.lower()).strip() for _, text in questions]
    assert len(normalized) == len(set(normalized)) == 160


def test_trial_bank_includes_every_required_evaluation_dimension():
    text = BANK.read_text()
    for dimension in (
        "Cross-platform",
        "Confluence",
        "Jira",
        "Slack",
        "Drive",
        "Controlled mutation",
        "Audit result",
        "Neutral no-answer",
        "Adversarial",
    ):
        assert dimension in text


def test_scorecard_keeps_security_and_honesty_gates():
    text = METRICS.read_text()
    for gate in (
        "Unauthorized content reaching model context",
        "Restricted-exists versus nonexistent response equivalence",
        "Real model path",
        "Tencent requirement",
        "must never be presented as end-to-end latency",
    ):
        assert gate in text
