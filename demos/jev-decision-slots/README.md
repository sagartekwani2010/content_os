# Jev decision slots — runnable carousel demo

This is the code handoff behind the **“Where Jev belongs in an LLM system”**
carousel. It demonstrates five bounded decision contracts:

1. model routing;
2. support triage;
3. RAG filtering;
4. tool gating; and
5. agent evaluation.

It is a small executable script, not an application. Run it from a Codex or
terminal session with Python 3. No packages are required.

## Show the contracts without a key

```bash
python demos/jev-decision-slots/run_demo.py --list
python demos/jev-decision-slots/run_demo.py model-routing
python demos/jev-decision-slots/run_demo.py --all
```

The default is a **dry run**. It prints the exact state and typed questions but
does not create a fake Jev response or claim a benchmark result. This is safe
to screen-record for the carousel's code-execution segment when explaining the
contract.

## Run a live call with your own Jev access

Never commit or screen-record a key. Configure it only in your terminal:

```bash
export TYPESAFE_API_KEY="your_key_here"
python demos/jev-decision-slots/run_demo.py model-routing --live
```

The default endpoint is `https://api.typesafe.ai/v1/systemone`. If your access
uses a different official provider or gateway, override the endpoint and model:

```bash
export JEV_API_URL="https://your-approved-provider.example/v1/systemone"
export JEV_API_KEY="your_key_here"
python demos/jev-decision-slots/run_demo.py tool-gate --live --model jev-1.13.0
```

The live mode prints the provider's raw JSON. Save that output as an experiment
artifact, then evaluate it on a labelled fixture suite before making claims
about quality, safety, cost or latency.

## What this demonstrates

Each fixture sends a supplied `state` plus typed questions. The questions use
three decision shapes:

- `choice`: one of a known set of routes;
- `score`: a position on an explicit ordered rubric; and
- `noul`: the probability of a specific yes/no proposition.

Your application—not Jev—must own permissions, policy enforcement, confidence
thresholds, fallbacks, audit logs and the actual action. A tool gate is not a
security system; a RAG relevance judgment is not proof that a claim is true;
an evaluator is not a substitute for a labelled test set.

## Screen-recording plan

1. Run `--list` for a one-second overview.
2. Run `model-routing` with no `--live`; zoom into `state` and `questions`.
3. Explain that the code receives a typed decision, then branches in code.
4. If live credentials are available, run **one** low-risk fixture with
   `--live` and show the raw result after checking it contains no secret or
   customer data.
5. Do not show a live result if you cannot label the model, endpoint, fixture
   version and run conditions.

## Claims to avoid

- The demo is not evidence that Jev is correct on these fixtures.
- Do not call it a safety, compliance, legal, financial or medical system.
- Do not repeat performance claims from a vendor benchmark as a product result.
