# ethos

Ethos is an evolution of context. MEP, the Model Ethos Protocol, is how an
owner's ethos is served to whatever they work in: their principles, their
practice, and the record of how those change over time.

MCP serves context to the model. MEP serves the person to the harness.

This repository is the public framework: the protocol, the reference server,
the forkable template, and the preference record spec. Anyone can clone it,
run their own ethos, and improve the protocol in the open.

## What an ethos is

Your agents already read files about you. Most of the time those files are
stale, scattered and impossible to check. An ethos is the same content made
honest:

- **Authored.** You (or your team) write it. No model prose, no generated
  values. Every entry is dated and attributed.
- **Versioned.** Preferences are immutable revision records in a causal
  graph. Corrections supersede, history is never rewritten, and rejections are
  recorded, not erased.
- **Checkable.** Every document is SHA-256 pinned end to end. Exports carry
  a manifest. A file that fails its hash is unverified, never assumed good.
- **Bounded.** Adaptation happens inside limits you can see and undo:
  a proposal never applies until you approve it, contested preferences apply
  nothing, and the learning switch persists.

## Three parts, three parents

| Part | From | What it contributes |
| --- | --- | --- |
| The corpus layout (`principles/`, `sops/`, `teams/`, `skills/`, `CHANGELOG.md`) | the Aska Digital corpus | The content model: dated, attributed, owned documents with change control |
| The serving framework (`mep/`) | [ahrazzle/soko](https://github.com/ahrazzle/soko) | Stdlib-only Python MCP server, path confinement, SHA-256 integrity, honest failure behavior |
| The adaptation philosophy | [weft-eido](https://github.com/Moissanite-Labs/weft-eido) | Bounded change. Respond to how the person actually works, inside limits they can see, check and undo. Condensation, not regeneration |
| The preference records | this repository, `v0.1/` | The v0.1 revision schema and fixtures |

## Use the template

Click "Use this template" on GitHub, or copy `template/` out of this
repository. Follow `template/README.md`. Your ethos is private by default;
publishing it is your explicit act.

```bash
git clone <your-ethos>
claude mcp add mep -- python3 -m mep --root /path/to/your-ethos serve
```

Or query it without any harness:

```bash
python3 -m mep --root /path/to/your-ethos status
python3 -m mep --root /path/to/your-ethos context "reviewing a contract" --budget 4000
```

## Install

```bash
pip install .
# or run from a checkout: python3 -m mep --help
```

Requires Python 3.10 or newer. No third-party packages.

## Verify this repository

```bash
python3 -m unittest discover -s tests -v
python3 v0.1/test_fixtures.py
python3 -m mep.integrity --root . --verify
```

## Repository layout

```
MEP.md          the protocol
v0.1/           the preference revision spec, schema, fixtures
mep/            the reference server (python3 -m mep)
template/       the forkable ethos skeleton
tests/          the test suite
CHANGELOG.md    dated record of every change and its reason
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Plain language, dated entries,
no personal data, no invented rules.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
