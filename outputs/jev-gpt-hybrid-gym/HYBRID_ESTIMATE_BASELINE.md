# Hybrid versus GPT-only — architecture estimate and provenance

## The comparison being shown

This Reel compares two deliberately traceable **two-step** model paths for the
same saved Gym check-in. It is not a claim that the hybrid beats an optimised
single-call GPT solution.

| Path | Step 1 | Step 2 | User response |
| --- | --- | --- | --- |
| GPT-only control | GPT-5.6 Sol interprets raw check-in into state | GPT-5.6 Sol chooses route and produces constrained response | Returned from the second GPT step |
| Hybrid | GPT-5.6 Sol interprets raw check-in into state | Jev judges risk and chooses `progress`, `hold`, `ask_for_data`, or `escalate` | Deterministic template for the locked route |

Both paths have the same schema validation and policy enforcement. A risk
signal is passed to the decision model in both paths; the policy layer blocks
any route that violates a hard boundary.

## Derived model-call estimate

The only input numbers are the previous Reel's matched public comparison:

| Component reference | GPT-5.6 Sol | Jev 1.13 |
| --- | ---: | ---: |
| Median latency per matched decision | 1,661 ms | 456 ms |
| Total cost for 2,390 matched decisions | $4.27 | $0.049 |
| Implied cost per decision | $0.001787 | $0.0000205 |

Assuming the two serial calls have the same per-call latency/cost profile as
that matched benchmark:

| System path | Estimated model-call latency | Estimated model-call cost | Relative to GPT-only |
| --- | ---: | ---: | ---: |
| GPT-only: Sol + Sol | 3,322 ms | $0.003573 | Baseline |
| Hybrid: Sol + Jev | 2,117 ms | $0.001807 | **36% lower latency; 49% lower cost** |

Calculations:

- latency: `(3,322 - 2,117) / 3,322 = 36.3%`;
- cost: `($0.003573 - $0.001807) / $0.003573 = 49.4%`.

## Strict disclosure for the Reel

The `36%` and `49%` values are a **SIMULATED ARCHITECTURE ESTIMATE**. They are
not recorded Gym Assistant performance and must not be called a live result.
They exclude non-model work such as network overhead, deterministic policy
checks and UI rendering. Those items must be captured in the real end-to-end
run.

The estimate also does **not** establish that a hybrid is always better. If a
single GPT call can safely understand, decide and respond in the product, that
one-call baseline can be faster and cheaper than a two-model path. The hybrid
only has a plausible advantage when it replaces a separately necessary,
repeated GPT decision step.

## Source boundary

The component inputs and their limitations are preserved in
`../jev-gpt-gym-benchmark-manual/SIMULATION_BASELINE.md`. The 2,390-item public
comparison is not fitness data and is not a measurement of this architecture.
Replace this estimate with raw hybrid and GPT-only logs before publishing a
performance result.
