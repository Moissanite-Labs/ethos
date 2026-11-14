# Security

## Reporting a vulnerability

Email the maintainers or open a private security advisory on this repository.
Do not open a public issue for anything that could help someone forge,
corrupt or exfiltrate an ethos.

Please include: what you found, how to reproduce it, and what an attacker
gains. We aim to acknowledge within 72 hours.

## Scope

- `mep/` and `v0.1/` code and fixtures
- The reference server's handling of paths, hashes and records
- The integrity manifest

## Out of scope

- Whether an owner chose to publish their own ethos. Exporting is documented
  as deliberate. An owner publishing their own data is using the feature.

## Design properties that help you

- Files outside the ethos root cannot be read through the server.
- A file that fails `SHA256SUMS` is reported as unverified, never served as
  trusted silently.
- Proposals never apply without the owner's decision.
- Rejected and deleted records carry no payload.
- Learning can be turned off by the owner at any time, and the switch is a
  file, not a flag in someone else's process memory.
