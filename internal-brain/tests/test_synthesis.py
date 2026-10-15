"""Model-written summaries: only sentences supported by the sources they cite survive."""
from app import synthesis
from app.identity import USERS

SRC = [{"ref": "S1", "platform": "jira", "title": "MIG-1", "passages": [
            {"text": "MIG-1 [In Progress] Epic: Postgres 12 to 16 migration."},
            {"text": "Status: 70% of tables migrated."}, {"text": "Cutover to Postgres 16 is planned for 20 Oct."}]},
       {"ref": "S2", "platform": "slack", "title": "#db-migration", "passages": [
            {"text": "@ravi: Blocker: replication lag on the orders table hit 40s during dual-write, so the migration cutover is on hold until MIG-2 is fixed."}]}]


def test_supported_sentences_are_kept():
    text = ("The Postgres 16 migration is in progress with 70% of tables migrated [S1]. "
            "Cutover is on hold until MIG-2 is fixed because replication lag on the orders table hit 40s [S2].")
    kept, dropped = synthesis.check(text, SRC)
    assert kept == text and dropped == []


def test_wrong_number_unknown_source_missing_citation_and_invented_claim_are_dropped():
    text = ("The migration is 90% done [S1]. "                       # number not in S1
            "Cutover is planned for 20 Oct [S3]. "                   # unknown source
            "The team is confident it will finish early. "           # no citation
            "The CEO approved a budget increase for the database vendor [S1]. "   # words not in the source
            "Cutover to Postgres 16 is planned for 20 Oct [S1].")    # fine
    kept, dropped = synthesis.check(text, SRC)
    assert kept == "Cutover to Postgres 16 is planned for 20 Oct [S1]." and len(dropped) == 4


def test_ticket_id_must_be_in_the_cited_source():
    kept, _ = synthesis.check("The cutover is blocked by MIG-7 [S2].", SRC)
    assert kept == ""


def test_disabled_without_a_configured_model():
    assert synthesis.enabled() is False
    assert synthesis.summarize("q", SRC)[0] is None


def test_brain_puts_a_checked_summary_on_top_and_keeps_the_extracts(brain, monkeypatch):
    monkeypatch.setattr(synthesis, "summarize", lambda q, sources: ("Short checked answer [S1].", {"mode": "summary_checked", "dropped": 1}))
    r = brain.ask(USERS["ravi"], "What was the root cause of the payment outage last quarter, and what follow-up tickets were created?")
    first, second, *rest = r["answer"].split("\n\n")
    assert first == "Short checked answer [S1]." and second.startswith("Evidence from ") and rest
    assert r["quality"]["mode"] == "model_summary"


def test_brain_without_summary_is_unchanged(brain):
    r = brain.ask(USERS["ravi"], "What was the root cause of the payment outage last quarter, and what follow-up tickets were created?")
    assert r["answer"].startswith("Here's what I found in ") and r["quality"]["mode"] == "extractive"


def test_reasoning_effort_is_sent_only_when_configured(monkeypatch):
    from app import llm
    monkeypatch.setattr(llm, "LLM_REASONING_EFFORT", "")
    assert "reasoning_effort" not in llm.request_body({"model": "m"})
    monkeypatch.setattr(llm, "LLM_REASONING_EFFORT", "none")
    assert llm.request_body({"model": "m"})["reasoning_effort"] == "none"


def _fake_model(monkeypatch, respond):
    import httpx
    from app import llm
    monkeypatch.setattr(llm, "LLM_PROVIDER", "openai_compatible")
    monkeypatch.setattr(llm, "LLM_BASE_URL", "https://model.example/v1")
    monkeypatch.setattr(llm, "LLM_MODEL", "test")
    monkeypatch.setattr(llm, "LLM_API_KEY", "fake")
    real = httpx.Client
    monkeypatch.setattr(llm.httpx, "Client", lambda **kw: real(transport=httpx.MockTransport(respond), **kw))
    return llm


def test_model_choosing_nothing_falls_back_to_extracts(monkeypatch):
    import httpx, json as _json
    llm = _fake_model(monkeypatch, lambda req: httpx.Response(200, json={"choices": [{"message": {"content": _json.dumps({"selections": []})}}]}))
    monkeypatch.setenv("IB_LLM_REQUIRE_LIVE", "0")
    r = llm.complete("Status?", [{"ref": "S1", "text": "Ready for cutover."}], "Jane")
    assert r.mode == "extractive_fallback" and r.reason == "model_selected_nothing" and "Ready for cutover." in r
    monkeypatch.setenv("IB_LLM_REQUIRE_LIVE", "1")                 # strict live runs still fail visibly
    import pytest
    with pytest.raises(llm.ModelUnavailable):
        llm.complete("Status?", [{"ref": "S1", "text": "Ready for cutover."}], "Jane")


def test_rate_limit_waits_longer_than_a_server_error(monkeypatch):
    from app import llm
    assert llm.backoff(429, 0) > llm.backoff(503, 0) and llm.backoff(429, 1) > llm.backoff(503, 1)
    slept = []
    monkeypatch.setattr(llm.time, "sleep", lambda s: slept.append(s))
    monkeypatch.setenv("IB_LLM_MIN_INTERVAL_S", "2")
    llm._last_call[0] = llm.time.monotonic()
    llm.pace()
    assert slept and 0 < slept[0] <= 2


def test_completion_claim_citing_an_open_ticket_is_dropped():
    src = [{"ref": "S5", "platform": "jira", "title": "PAY-2", "passages": [
                {"text": "PAY-2 [In Progress] Alert when any certificate expires within 14 days."}, {"text": "Add expiry alerting."}]},
           {"ref": "S6", "platform": "jira", "title": "PAY-3", "passages": [
                {"text": "PAY-3 [Done] Make cert renewal job fail loudly."}, {"text": "Renewal job now pages on failure."}]}]
    seen_live = "To address this, we implemented expiry alerts for certificates within 14 days and updated the renewal job to page on failure [S5][S6]."
    assert synthesis.check(seen_live, src)[0] == ""
    ok = "The renewal job now pages on failure [S6]. Expiry alerting is in progress [S5]."
    assert synthesis.check(ok, src)[0] == ok
