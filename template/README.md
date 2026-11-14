# my-ethos

A personal ethos, served as a Model Ethos Protocol (MEP) instance. This
directory layout is the part anyone forking the [ethos
template](https://github.com/Moissanite-Labs/ethos) gets on day one: the
documents, the change log, and the `.mep/` revision store.

Ethos text is context, not authority. Your agents read this. None of it grants
any of them permission to act beyond what you separately authorize.

## Make it yours

1. Use this repository as a template on GitHub ("Use this template"), or copy
   this directory out of the ethos repository.
2. Rename the repo and the `name` in `ethos.json`.
3. Replace the example documents in `principles/` with your own. Date every
   change in `CHANGELOG.md` with the reason. Keep attribution.
4. Point your harnesses at it:

   ```bash
   git clone <your-ethos-repo>
   claude mcp add mep -- python3 -m mep --root /path/to/your-ethos serve
   ```

   Or query it directly:

   ```bash
   MEP_ROOT=/path/to/your-ethos python3 -m mep status
   MEP_ROOT=/path/to/your-ethos python3 -m mep context "writing an incident report" --budget 3000
   ```

## Layout

| Path | What it holds |
| --- | --- |
| `principles/` | Rules that apply to everything you do with agents. |
| `sops/` | Step-by-step practice for recurring work. |
| `teams/` | Rules for one team or family of agents only. |
| `skills/` | Shared skills, with their own credit and license. |
| `docs/` | Longer references, evidence and provenance notes. |
| `.mep/` | The preference revision store: `revisions/` (canonical), `proposals/` (pending your decision), `approvals.json` (your approvals). |
| `ethos.json` | Instance metadata served by `ethos_capabilities`. |
| `CHANGELOG.md` | Dated record of every change and its reason. |

## The rules that keep this honest

- Private by default. An ethos is about you. Publishing it is your explicit act.
- No secrets, no personal data of others, no machine-specific paths.
- Preferences are records, not edits. Corrections supersede. History stays.
- A proposal your agent makes never applies until you approve it.
- `python3 -m mep.integrity --root . --verify` checks the tree against
  `SHA256SUMS`. Re-write the manifest only with `--write` after you review a change.

Loaded through MEP, this ethos answers `ethos_context`, `ethos_query`,
`ethos_status` and the rest. See [MEP.md](../MEP.md) in the template for the
protocol.
