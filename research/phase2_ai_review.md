# Phase 2 blinded AI-assisted review

Use Nemotron for optional development and challenge ambiguity diagnostics. Preserve independent human judgments in the human review workflow. AI judgments are advisory and have separate provenance.

## Local preparation

```powershell
python -m src.phase2_review prepare --split development --output results/private/ai-review/development-packet
python nemotron_review.py --prepare-blinded development results/private/ai-review/development-packet/review.jsonl --output results/private/ai-review/development-requests
```

Use `challenge` and fresh paths for the 18 challenge cases. The connector checks the exact canonical packet and stages one chat request per case in `requests.jsonl`. Each request contains the rubric and only the opaque ID, fictional policy and ordered dialogue. The local manifest records AI provenance, group, case count and packet/request digests. Preparation never loads credential configuration. Keep files under ignored `results/private/`. The command supports only development and challenge.

## After external use is authorized

Use an approved private executor to submit each JSON line as a separate request with reviewed model and provider settings. Keep credentials in the environment or ignored `.env` and send them only in the authorization header. The existing connector pins the OpenRouter endpoint, refuses redirects and restricts generic review to `nvidia/*nemotron*:free`. Its generic file critique command truncates inputs. The staged workflow requires an executor that preserves each message exactly.

Privately record model, provider/settings, date, request digest, failures and retries. Save responses with AI-assisted provenance. Check the returned opaque ID against its request and enforce the four fields and types in the reviewer rubric. Record missing or malformed outputs as unresolved. Keep disagreement reports private because combining their IDs with binary responses can reveal draft labels. Preserve independent reviewers' first-pass blindness to AI judgments and detector predictions.

## Connector and file inventory

The credential and paid-model guards were checked with mocks. This preparation produced zero remote responses.

| File | Disposition |
| --- | --- |
| `prompts/NEMOTRON.md` | Active dependency of the generic critique command. |
| `AGENTS.md`, `nemotron_review.py`, `notes/ai_usage.md` | Current operating contract, connector and research provenance. |

The two manual kickoff prompts were retired. The repository contract and task board carry current instructions.
