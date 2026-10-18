# N05 specification

Implement small independently invocable Power Automate workers with persistent
Dataverse case/check state. Deterministic checks precede optional interpretation;
a failing worker cannot discard completed siblings. No single flow lifetime is
the lifetime of a credentialing case.

Owner: Approve maintainer. Reuse existing check/job kernels as behavioural tests,
not a claim of native scheduler deployment. Acceptance: plan.md tasks including
safe corrections, concurrency, technical exception routing and AI-off operation.
