# YieldGPT video: lines by speaker (about 5:30 total)

Generated from `VIDEO_SCRIPT.md`, which has setup and editing notes. Blocks are in running order.
Blockquotes are what you say; the rest is what to click or show.

## Mohnish (about 1:56)

### 0:00 to 0:40 · Slides 1 and 2 (title, the problem)

*Cue: you open the video.*

> We're YieldGPT, for Aspire's Internal Brain case study, built with Tencent's CodeBuddy and
> WorkBuddy. Company knowledge lives in Confluence, Jira, Slack and Drive, each with its own
> permission rules. Copy it all into one AI index and the assistant can leak what people were never
> allowed to open, and nobody can prove who saw what.

### 2:45 to 3:30 · LIVE DEMO B: revoke access on the real Confluence site

*Cue: after Punya finishes.*

App as **Ravi Menon**. Ask: **"What's the latest runbook for the payment-service incident?"**

> Ravi gets the runbook from our live Confluence.

Confluence tab: **•••** > **Restrictions** > "Only specific people can view or edit" > add **Asha** > **Apply**.
Back to the app, same question as Ravi.

> I restrict the page in Confluence, with no reindexing, and on his very next question it's gone.

**After recording:** remove the restriction.

### 4:05 to 4:30 · Slides 8, 9, 10 (proof)

*Cue: after Punya finishes the audit demo (you go first of three).*

> On a real Atlassian site, 84 of 84 permission decisions matched Atlassian.

### 4:50 to 5:15 · How we built it with CodeBuddy / WorkBuddy

*Cue: after Punya finishes slide 11 (you go first of three).*

Show your CodeBuddy or WorkBuddy screenshot. About 8 seconds, one sentence: what you used it for, and one tip. Say only what you actually did:

> [fill in]

### 5:15 to 5:30 · Slides 12 and 13 (close)

*Cue: after Punya's CodeBuddy line.*

> Confluence and Jira are live, answers are checked, and Hunyuan, live Slack and Drive come next.
> YieldGPT: ask once, see only what you may, and prove it afterwards.

## Imaad (about 1:41)

### 0:40 to 1:15 · Slides 3 and 4 (what it does, six checks animation)

*Cue: after Mohnish finishes.*

> YieldGPT never copies permissions. You ask once, and each platform decides, live, as you. Every
> source passes six checks, from before we read it to when you open a citation. Anything denied
> drops out, gets recorded, and looks exactly like something that never existed.

### 1:15 to 2:05 · LIVE DEMO A: one question, four platforms

*Cue: continue straight on.*

App as **Jane Doe**. Ask: **"What's blocking the database migration?"**

> Plain English, one question. The AI answer comes first, every sentence checked against its
> sources, here our real Jira ticket MIG-2 and the team's Slack thread. (Name what's on screen.)

Sign in as **Kim Lee**. Ask: **"Show me the security incident report from the Q3 breach"**.

> Kim's a contractor. She gets a neutral answer: no title, no hint the report exists.

### 4:05 to 4:30 · Slides 8, 9, 10 (proof)

*Cue: after Punya's proof line.*

> With a real model, 71 of 78 cases and zero unauthorized citations.

### 4:50 to 5:15 · How we built it with CodeBuddy / WorkBuddy

*Cue: after Mohnish's CodeBuddy line.*

Show your CodeBuddy or WorkBuddy screenshot. About 8 seconds, one sentence: what you used it for, and one tip. Say only what you actually did:

> [fill in]

## Punya (about 1:51)

### 2:05 to 2:45 · Slides 5 and 6 (architecture, the model)

*Cue: after Imaad finishes.*

> The platforms decide access, our server runs every check, and the model is untrusted: it only
> sees passages that already passed, and any sentence the sources don't support is dropped.
> For this proof of concept we used Google's free Gemini API, which is widely used and standard for
> prototyping. It goes through the same OpenAI-compatible interface Tencent Hunyuan offers, so
> switching to Hunyuan is just a URL, model name and key.

### 3:30 to 4:05 · Slide 7 (audit) + LIVE DEMO C

*Cue: after Mohnish finishes.*

App as **Priya Nair**, **/compliance**, type:
**"Show me everything user 'ravi' accessed related to the 'payment-gateway' Confluence space in the last 30 days"**

> Compliance asks in plain English and sees every request, every decision and every answer, all
> hash-chained. And no checkpoint, no answer.

### 4:05 to 4:30 · Slides 8, 9, 10 (proof)

*Cue: after Mohnish's proof line.*

> Under load, 25 users for five minutes, zero leaks and zero audit gaps.

### 4:30 to 4:50 · Slide 11 (Tencent ecosystem)

*Cue: after Imaad's proof line.*

> Built with CodeBuddy, usable inside WorkBuddy through our MCP connector, Hunyuan-ready, and
> packaged for Tencent Cloud.

### 4:50 to 5:15 · How we built it with CodeBuddy / WorkBuddy

*Cue: after Imaad's CodeBuddy line.*

Show your CodeBuddy or WorkBuddy screenshot. About 8 seconds, one sentence: what you used it for, and one tip. Say only what you actually did:

> [fill in]
