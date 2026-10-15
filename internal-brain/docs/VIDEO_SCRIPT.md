# YieldGPT demo video script (target 5:30; the handbook requires 5 to 8 min)

Plays along with the deck (`docs/deck/index.html`, press F for fullscreen, arrow keys to advance)
with three live app segments in between. Voices: **M** = Mohnish, **I** = Imaad, **P** = Punya.
Every number below comes from a dated report in `evaluation/reports/`.

On-screen caption for the whole video (bottom corner):
**"Live: Confluence + Jira (Atlassian Cloud) · Simulated: Slack, Drive · Model: Gemini free tier (Hunyuan-compatible)"**

---

## Project description (also for the submission form)

**What it is.** YieldGPT is an internal knowledge assistant for Company A, Aspire's "Internal Brain"
case study. An employee asks one question in plain English and gets one cited answer drawn from
Confluence, Jira, Slack and Google Drive, built only from what that person is allowed to open right
now, with every retrieval and answer recorded in a tamper-evident audit trail.

**The pain.** Knowledge is scattered across four platforms with four different permission models.
The brief estimates Company A's staff lose about 30% of their week searching. Assistants that copy
everything into one index can leak what people were never allowed to see, and nobody can prove who
saw what.

**How it works.** Each platform decides access itself, live, as the asking user: before reading,
after reading, before release, and again when a citation is opened. Denied content looks exactly like
content that doesn't exist. Only authorized passages reach the model. The model picks evidence and
writes a short answer; a deterministic checker keeps a sentence only if its facts, numbers, ticket ids
and statuses are in the sources it cites. Every decision is hash-chained and anchored to two
write-once stores; no checkpoint, no answer.

**How prompts drive the AI.** Two prompts: one asks the model to select evidence passages by id
(it returns JSON, never prose); the second asks for a 1 to 4 sentence answer from those passages only,
citing each sentence, copying numbers exactly and keeping ticket statuses exact. Source text is
declared untrusted data, never instructions.

**Business value.** One place to ask instead of four searches; no new leak surface; a compliance
officer can answer "who saw this document?" in seconds. Proven live on a real Atlassian site:
84/84 permission decisions matched Atlassian, 14/14 brief scenarios, 21/21 lifecycle steps; 0
unauthorized citations across every run.

---

## Before recording (10 minutes)

1. Cloudflare WARP **off**. `.env`: `IB_LLM_PROVIDER=openai_compatible`, model `gemini-3.1-flash-lite`.
2. `cd internal-brain && python scripts/reset_demo.py`, then
   `IB_ATLASSIAN_MODE=live IB_ACCOUNT_MAP=accounts.json python -m uvicorn app.server:app --port 8000`.
3. Tabs: deck · app (http://127.0.0.1:8000) · Confluence runbook page (no restrictions) · one
   CodeBuddy chat per person · WorkBuddy with the YieldGPT connector (if #17 is merged).
4. Ask each demo question once to warm up; wait a minute so the free tier's per-minute limit resets.
5. 1080p, browser zoom 125%, notifications off.

---

## 0:00 to 0:40 · Slides 1 and 2 (title, the problem) · M

> We're YieldGPT, for Aspire's Internal Brain case study, built with Tencent's CodeBuddy and
> WorkBuddy. Company knowledge lives in Confluence, Jira, Slack and Drive, each with its own
> permission rules. Copy it all into one AI index and the assistant can leak what people were never
> allowed to open, and nobody can prove who saw what.

## 0:40 to 1:15 · Slides 3 and 4 (what it does, six checks animation) · I

> YieldGPT never copies permissions. You ask once, and each platform decides, live, as you. Every
> source passes six checks, from before we read it to when you open a citation. Anything denied
> drops out, gets recorded, and looks exactly like something that never existed.

## 1:15 to 2:05 · LIVE DEMO A: one question, four platforms · I

App as **Jane Doe**. Ask: **"What's blocking the database migration?"**

> Plain English, one question. The AI answer comes first, every sentence checked against its
> sources, here our real Jira ticket MIG-2 and the team's Slack thread. (Name what's on screen.)

Sign in as **Kim Lee**. Ask: **"Show me the security incident report from the Q3 breach"**.

> Kim's a contractor. She gets a neutral answer: no title, no hint the report exists.

## 2:05 to 2:45 · Slides 5 and 6 (architecture, the model) · P

> The platforms decide access, our server runs every check, and the model is untrusted: it only
> sees passages that already passed, and any sentence the sources don't support is dropped.
> For this proof of concept we used Google's free Gemini API, which is widely used and standard for
> prototyping. It goes through the same OpenAI-compatible interface Tencent Hunyuan offers, so
> switching to Hunyuan is just a URL, model name and key.

## 2:45 to 3:30 · LIVE DEMO B: revoke access on the real Confluence site · M

App as **Ravi Menon**. Ask: **"What's the latest runbook for the payment-service incident?"**

> Ravi gets the runbook from our live Confluence.

Confluence tab: **•••** > **Restrictions** > "Only specific people can view or edit" > add **Asha** > **Apply**.
Back to the app, same question as Ravi.

> I restrict the page in Confluence, with no reindexing, and on his very next question it's gone.

**After recording:** remove the restriction.

## 3:30 to 4:05 · Slide 7 (audit) + LIVE DEMO C · P

App as **Priya Nair**, **/compliance**, type:
**"Show me everything user 'ravi' accessed related to the 'payment-gateway' Confluence space in the last 30 days"**

> Compliance asks in plain English and sees every request, every decision and every answer, all
> hash-chained. And no checkpoint, no answer.

## 4:05 to 4:30 · Slides 8, 9, 10 (proof) · M, P, I

> **M:** On a real Atlassian site, 84 of 84 permission decisions matched Atlassian.
> **P:** Under load, 25 users for five minutes, zero leaks and zero audit gaps.
> **I:** With a real model, 71 of 78 cases and zero unauthorized citations.

## 4:30 to 4:50 · Slide 11 (Tencent ecosystem) · P

> Built with CodeBuddy, usable inside WorkBuddy through our MCP connector, Hunyuan-ready, and
> packaged for Tencent Cloud.

## 4:50 to 5:15 · How we built it with CodeBuddy / WorkBuddy · all three, ~8 s each

Show your CodeBuddy or WorkBuddy screenshot. **Say only what you actually did**, one sentence each:
what you used it for, and one tip.

- M: [fill in]
- I: [fill in]
- P: [fill in]

## 5:15 to 5:30 · Slides 12 and 13 (close) · M

> Confluence and Jira are live, answers are checked, and Hunyuan, live Slack and Drive come next.
> YieldGPT: ask once, see only what you may, and prove it afterwards.

---

## Editing notes

- Trim waits, but never cut between the Confluence restriction and Ravi's next question.
- Blur emails, account ids, tokens, API keys and the site URL bar.
- If the free model tier rate-limits mid-recording, the app shows the exact extracts instead
  ("Evidence extracts" label). Re-record that segment rather than editing the label away.
