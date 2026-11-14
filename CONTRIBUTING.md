# Contributing

Thanks for helping make ethos boring in the good way: predictable, checkable,
and honest about its limits.

## What this repository is

The public framework for an anyone-can-use ethos: the protocol (`MEP.md`),
the preference revision spec (`v0.1/`), the reference server (`mep/`), and
the template (`template/`). It is not a personal ethos. Do not add anyone's
private preferences here, yours included.

## Ground rules

- Plain language. Short sentences. No jargon without a plain sentence around
  it. If a careful second-language reader cannot follow it, rewrite it.
- Date every rule you add or change, and say why in `CHANGELOG.md`.
- State rules as rules. Do not invent rules. If something is unclear, write
  it down marked `TODO(owner)` instead of guessing.
- Never add personal data, secrets, credentials, or machine-specific paths.
- Keep attribution. Work contributed here keeps its credit in `NOTICE`.
- No third-party Python dependencies in `mep/`. Standard library only, on
  purpose.
- No CI workflows yet. Until one exists, run the three checks from README.md
  before sending a PR.
- Docs PRs need no independent code review. The author may merge their own
  once in good shape. Code PRs to `mep/` or `v0.1/` get one reviewer.
- Merge with squash and a clean, hand-written message. No force-push, no
  history rewrites.

## How to propose a protocol change

Open an issue first with the problem, not the solution. If the change touches
`v0.1/`, expect a schema discussion before code. Protocol changes bump
`MEP_VERSION` or `SPEC_VERSION` and land in `CHANGELOG.md` with the reason.

## Credit

Contributions are Apache-2.0 by default. Add your name or handle to the
credits in your PR description if you want it recorded in `NOTICE`.
