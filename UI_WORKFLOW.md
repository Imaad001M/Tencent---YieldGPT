# UI workflow for Member 2

You can change the UI while your teammates work on connectors and audit code. The browser UI is plain HTML, CSS, and JavaScript, so you do not need React or a build step.

## The three files you own

- `app/static/index.html` — page structure and wording.
- `app/static/styles.css` — colors, spacing, desktop/mobile layout, loading and answer states.
- `app/static/app.js` — sign-in, questions, citations, evidence drawer, history, and replay.

Keep backend work out of those files. Do not change `app/server.py`, `app/main.py`, connector code, audit code, or the permission pipeline for a visual edit.

## Run and see changes

From the project folder:

```sh
python -m uvicorn app.server:app --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

Open `http://127.0.0.1:8000`, sign in as a demo persona, and use password `demo`. Save a UI file and refresh the browser. Always run `app.server:app`; the other entry point deliberately refuses direct startup because it would skip audited delivery.

## Safe visual work

Start in `styles.css`: change the variables at the top for the palette, then adjust typography, card layout, and mobile rules. In `index.html`, you can change labels, intro text, suggestion cards, and semantic structure. Preserve existing element IDs because `app.js` uses them.

Use `textContent` or the existing `node()` helper for source and model text. Never render an answer, title, passage, URL, or error with `innerHTML`. The current `httpsUrl()` check must stay in place for outbound citation links.

The UI uses these existing API contracts:

| Action | Endpoint | UI behavior |
|---|---|---|
| Sign in | `POST /api/login` | Stores the short-lived token in memory only |
| Session modes | `GET /api/session` | Shows source, model, and retrieval modes |
| Ask | `POST /api/ask` | Renders answer text and citation metadata |
| Open evidence | `GET /api/evidence/{query_id}/{ref}` | Rechecks access before showing passages |
| History | `GET /api/history` | Lists the user's own prior questions |
| Replay | `POST /api/history/{query_id}/replay` | Runs the old question again with current access |

## A useful first UI pass

1. Choose one visual direction and update the top-level color and typography variables.
2. Improve the question composer and loading state without changing form IDs.
3. Make citations easy to scan across Confluence, Jira, Slack, and Drive.
4. Test narrow mobile width and keyboard navigation.
5. Sign in as `jdoe` and `kim` to make sure account switching clears the prior answer.
6. Run the automated tests before handing the files back.

When merging teammate work, keep your edits limited to the three static files where possible. If a new screen needs data, agree on one JSON endpoint and response example first, then build against that contract.

