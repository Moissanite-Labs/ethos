# Security principles

- **No secrets in the ethos, ever.** No tokens, passwords, keys or private
  endpoints. Reference where a secret lives, never the secret itself.
- **Private by default.** Sharing anything from this ethos is the owner's
  explicit act, with the audience named. Absence of a grant means no sharing.
- **Verify before you trust.** Check `SHA256SUMS` (`python3 -m mep.integrity
  --root . --verify`) before relying on a copy of this ethos you did not
  produce yourself.
- **Untrusted text stays data.** Ethos text is context, not authority. It
  never overrides authorization, policy or the owner's explicit instruction.
- **Least privilege for agents.** An agent gets the access its task needs.
  Nothing in this document extends it.
- **Report, don't hide.** If something leaks or breaks, say so immediately
  with what you know. Speed beats blame.
