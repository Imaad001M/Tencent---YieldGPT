# YieldGPT video: lines by speaker

Generated from `VIDEO_SCRIPT.md` (the full script, with setup and editing notes). Each block is in
running order. The cue line says who speaks just before you. Blockquotes are what you say; the rest
is what to click or show.

## Mohnish (about 2:45 speaking)

### 0:00 to 0:30 · Slide 1 (title)

*Cue: you open the video.*

> We're YieldGPT, for Aspire's Internal Brain case study. One question across Confluence, Jira,
> Slack and Google Drive, answered only from what you're allowed to see, and every answer on the
> record. I built the permissions and connectors, Imaad the retrieval, answers and UI, and Punya the
> audit trail and deployment. We built it with Tencent's CodeBuddy and WorkBuddy.

### 0:30 to 1:00 · Slide 2 (the problem)

*Cue: continue straight on from your previous block.*

> Company knowledge lives on four platforms, each with its own permission rules: space and page
> restrictions in Confluence, issue security in Jira, private channels in Slack, folder sharing in
> Drive. Copy it all into one AI index and the assistant can show people what they were never
> allowed to open, and nobody can prove afterwards who saw what.

### 3:55 to 4:55 · LIVE DEMO B: revoke access on the real Confluence site

*Cue: after Punya finishes.*

App as **Ravi Menon**. Ask: **"What's the latest runbook for the payment-service incident?"**

> Ravi's on call for payments. The runbook comes from our live Confluence.

Confluence tab, on the runbook page: **•••** > **Restrictions** > "Only specific people can view or
edit" > add **Asha** > **Apply**.

> I've restricted the page in Confluence. We reindex nothing.

App, same question as Ravi.

> Gone, on the very next question. In our measured live run that took 0.27 seconds, and it never
> came back. Asha still sees it, because Confluence still allows her.

**After recording:** remove the restriction.

### 5:35 to 5:50 · Slide 8 (proof, live)

*Cue: after Punya finishes.*

> On a real Atlassian Cloud site: 84 of 84 permission decisions matched Atlassian, 14 of 14 brief
> scenarios passed, and 21 of 21 lifecycle steps, including an inherited page restriction.

### 6:40 to 7:10 · How we built it with CodeBuddy / WorkBuddy

*Cue: after Punya finishes.*

Show your CodeBuddy or WorkBuddy screenshot. About 10 seconds. Say only what you actually did:

- What you asked CodeBuddy/WorkBuddy to do: [fill in]
- What worked: [fill in]
- One tip for other developers: [fill in]

Then the team line:

> We split the build into three owners with no shared files, so our coding agents could work in
> parallel without stepping on each other, and every change had to pass the full test suite first.

### 7:10 to 7:30 · Slides 12 and 13 (honest status, close)

*Cue: after the team finishes.*

> What's live and verified: Confluence and Jira on a real site, real model answers checked sentence
> by sentence, write-once checkpoints, and the full test suite on every pull request. Next: Hunyuan
> benchmarked on our evaluation, live Slack and Drive, and a public URL on Tencent Cloud.
>
> YieldGPT. Ask once. See only what you may. Prove it afterwards.

## Imaad (about 2:15 speaking)

### 1:00 to 1:25 · Slide 3 (what it does)

*Cue: after Mohnish finishes.*

> So YieldGPT never copies permissions. You ask once; each platform decides, live, as you; and
> everything goes on the record. On our real Jira site, PAY-4 sits behind a security level: Ravi
> can browse the project and is still denied, Asha gets it. Jira made that call, not us.

### 1:25 to 1:50 · Slide 4 (six checks, let the animation run)

*Cue: continue straight on from your previous block.*

> Every candidate passes six checks: a prefilter that can only remove, a live check before reading,
> again after reading, again before release, and once more when you open a citation. Anything denied
> drops out, is recorded, and looks exactly like something that never existed.

### 1:50 to 2:55 · LIVE DEMO A: one question, four platforms

*Cue: continue straight on from your previous block.*

App. Sign in as **Jane Doe**. Ask: **"What's blocking the database migration?"**

> Jane's a backend engineer. Plain English, one question. The AI answer comes first, and every
> sentence is checked against the sources it cites. Below are the sources it used, here the
> blocked ticket MIG-2 from our real Jira and the engineers' Slack thread. (Name what's on screen.)

Click the **MIG-2** source: passages, version, Open in Jira.

> Opening a citation re-checks access. The private leads channel Jane isn't in never appears.

Sign in as **Kim Lee** (contractor). Ask **"Show me the security incident report from the Q3 breach"**,
then **"Show me the unicorn migration to mars report"**.

> Kim has no Atlassian account. Same neutral answer for a report that exists and one that doesn't.
> No title, no hint.

### 6:00 to 6:10 · Slide 10 (proof, answer quality)

*Cue: after Punya finishes.*

> And with a real model in the loop: 71 of 78 evaluation cases, zero unauthorized citations, ten of
> ten attacks resisted. Every number has a date and a label: live, fixture or synthetic.

### 6:40 to 7:10 · How we built it with CodeBuddy / WorkBuddy

*Cue: after Punya finishes.*

Show your CodeBuddy or WorkBuddy screenshot. About 10 seconds. Say only what you actually did:

- What you asked CodeBuddy/WorkBuddy to do: [fill in]
- What worked: [fill in]
- One tip for other developers: [fill in]

## Punya (about 2:30 speaking)

### 2:55 to 3:20 · Slide 5 (architecture)

*Cue: after Imaad finishes.*

> Four trust boundaries. The platforms are the source of truth for access. Our server runs every
> check and writes the audit. The language model is untrusted. And the write-once checkpoint stores
> can't be rewritten, even by us.

### 3:20 to 3:55 · Slide 6 (the model)

*Cue: continue straight on from your previous block.*

> The model only ever sees passages that already passed the checks. It holds no credentials and
> calls no tools, and any sentence it writes that the sources don't support is dropped.
>
> For this proof of concept we used Google's Gemini API on its free tier. It's widely used, free to
> start with, and standard practice for prototyping. Our model layer speaks the OpenAI-compatible
> API that Tencent Hunyuan also offers, so moving to Hunyuan is a configuration change: the URL, the
> model name and the key. The prompts, checks and permissions stay exactly the same.

### 4:55 to 5:35 · Slide 7 (audit) + LIVE DEMO C

*Cue: after Mohnish finishes.*

Slide 7, let the chain animation break once.

> Every decision is hash-chained. Edit one row and every link after it breaks. And no checkpoint, no
> answer: if we can't record it on two write-once stores, the user gets a refusal, never an
> unrecorded answer.

App as **Priya Nair**, open **/compliance**, type:
**"Show me everything user 'ravi' accessed related to the 'payment-gateway' Confluence space in the last 30 days"**

> Priya from compliance asks in plain English and gets each request: the question, every
> per-document decision, and the answer. Ravi was allowed the first time and denied after the
> restriction.

### 5:50 to 6:00 · Slide 9 (proof, under load)

*Cue: after Mohnish finishes.*

> Under load, 25 users for five minutes: 19,223 answers, zero permission leaks, zero audit gaps.

### 6:10 to 6:40 · Slide 11 (Tencent ecosystem)

*Cue: after Imaad finishes.*

> YieldGPT is built for Tencent's ecosystem. We built it with CodeBuddy. It runs inside WorkBuddy:
> an MCP connector lets you ask YieldGPT from a WorkBuddy or CodeBuddy chat, with every permission
> check still applied. Hunyuan drops in through the same OpenAI-compatible interface. And it's
> packaged for Tencent Cloud, where COS makes a natural second write-once anchor.

If the WorkBuddy connector is merged, cut in a 5-second clip of a WorkBuddy chat asking YieldGPT.

### 6:40 to 7:10 · How we built it with CodeBuddy / WorkBuddy

*Cue: continue straight on from your previous block.*

Show your CodeBuddy or WorkBuddy screenshot. About 10 seconds. Say only what you actually did:

- What you asked CodeBuddy/WorkBuddy to do: [fill in]
- What worked: [fill in]
- One tip for other developers: [fill in]
