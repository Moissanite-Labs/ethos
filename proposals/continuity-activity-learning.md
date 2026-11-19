# Proposal: continuity and learning from computer use

**Status: research proposal.** No capture adapter, permission, synchronization service, or live observation is enabled by this document. The Ethos v0.1 specification remains a draft; this proposal does not amend its wire format or claim implemented interoperability.

## Founder direction

The founder wants Exo to preserve context between sessions as one continuous memory, rather than treating each thread as an isolated task. The founder also wants Exo and Ethos to learn from a person's computer use so the assistant can adapt more closely to that person. This document explores how those goals might fit together; the safeguards and sequence below are design proposals for review, not additional statements of founder intent.

Exo's existing [memory model](https://github.com/Moissanite-Labs/exo/blob/main/docs/MEMORY-MODEL.md) describes continuity and private-thread boundaries. Ethos's [preference interchange proposal](../v0.1/SPEC.md) describes user-controlled preferences across harnesses. They have different jobs: memory can preserve context from authorized sessions; Ethos can represent selected, inspectable preferences derived from permitted evidence. Neither shared memory nor a preference is a grant to observe a device, synchronize data, publish content, or take an action. This proposal does not claim that a ChatGPT computer-history plugin is available to Exo or depend on its implementation.

## Proposed design requirements to evaluate

1. **Explicit, scoped opt-in.** A source adapter must remain off until the user deliberately enables that source, understands its scope, and can pause or revoke it. Memory continuity alone does not enable observation. Define separate permissions per source, device, and use; respect Exo's private-thread boundaries and prevent other people's activity from being captured without an appropriate basis.
2. **Local minimization and exclusions.** Explore processing locally and retaining the minimum necessary signal. Let users exclude apps, domains, windows, times, and activity categories before collection. Design to avoid capturing credentials, authentication material, private messages, and other sensitive content; evaluate how to avoid inferring sensitive attributes, not just storing their raw inputs. The precise taxonomy and platform controls are open.
3. **Retention and deletion.** Provide inspectable retention limits and a way to remove local observations and derived preferences. Explain what has been deleted and what cannot be recalled from previously exported copies. Ethos's tombstone and ancestry rules are distinct from deletion of raw observations: reconcile those requirements explicitly before implementation. No retention period is selected here.
4. **Evidence and user control.** Keep observations separate from inferred preferences. For each proposed learning, show a meaningful, privacy-preserving source reference, scope, confidence, and reason for the inference. Let the owner inspect, correct, reject, or delete it. Do not silently replace an owner-confirmed explicit preference with an inference; follow the existing Ethos approval and conflict requirements.
5. **Synchronization and publication.** Keep records private by default. Synchronization to each authorized harness or device is separately enabled and revocable; disabling it stops future transfers but cannot guarantee retrieval of copies already sent. Publishing is a separate, explicit decision. Evaluate a requirement that raw computer activity is never published and that only individually selected, reviewed derived preferences can be shared.
6. **Preferences are not authority.** Observations and learnings are untrusted context, not executable instructions or permission for an agent to access data, communicate, spend, change settings, or act. Source, memory, synchronization, and action permissions must remain separate.

These requirements need threat modeling, usability testing, and platform-specific feasibility review. They do not imply that collection can be made complete or perfectly safe, or that an observed habit is a reliable preference.

## Bounded first prototype and evaluation

Use **synthetic, hand-authored fixtures only**. Do not enable live device capture or connect a real computer-history source for this prototype.

1. Model a disabled-by-default source and a few fictional, non-sensitive activity summaries. Exercise enable, exclusion, pause, and revoke states without reading any actual device history.
2. Derive a candidate preference as an inference with source reference, scope, and confidence; show it to a user for correction or rejection. Keep the synthetic observation and preference in separate stores or models. Demonstrate that an explicit user preference is not overwritten by an unapproved inference.
3. Simulate two harnesses using the Ethos revision model. Demonstrate authorized private export/import, a conflict or rejection, stopping future transfer after revocation, and the limitation that an already exported copy may remain. Do not mistake a simulation for a real adapter or an authorization system.
4. Evaluate with negative cases: disabled source, excluded category, sensitive fixture, missing or withdrawn authorization, attempted raw publication, contested preference, and a preference presented as an instruction. Each must be rejected or withheld as appropriate. Verify that ordinary cross-session context can be used only within the existing memory and private-thread boundaries.
5. Review utility, false inferences, provenance clarity, deletion and revocation behavior, and the burden of inspection. Record assumptions and gaps. Continue to a separately reviewed design only if users can understand and control the flow and the evidence shows a useful benefit; otherwise revise or stop.

## Open decisions

- Which sources, platforms, permission models, and exclusion controls are feasible and understandable?
- How are sensitive categories and inferences identified, and what happens when a source cannot enforce an exclusion?
- What is stored locally, for how long, and how do observation deletion, preference tombstones, backups, exports, and revocation interact?
- What evidence is enough for a learning, how is confidence calibrated, and when is owner approval required before use?
- How should separate devices and harnesses authenticate, synchronize, resolve conflicts, and communicate revocation without conflating identity, consent, or authorization?
- How are private threads, shared devices, other people's information, and enterprise or multi-user contexts handled?
- What evaluation demonstrates benefit without live capture, and what independent review and user authorization would be needed before any live pilot?
