"""MEP - Model Ethos Protocol.

Ethos is an evolution of context. MCP serves context to a model; MEP serves
an owner's ethos to whatever harness they are working in: their principles,
their practice, and the record of how those change over time.

This package is the reference implementation. Python 3.10+, standard library
only. See MEP.md for the protocol.
"""

from __future__ import annotations

__version__ = "0.1.0"

MEP_VERSION = "0.1"
SPEC_VERSION = "0.1"

SERVER_INFO = {
    "name": "mep",
    "version": __version__,
}

SUPPORTED_PROTOCOLS = [
    "2024-11-05",
    "2025-03-26",
    "2025-06-18",
    "2025-11-25",
    "2026-07-28",
]

SERVER_INSTRUCTIONS = (
    "MEP (Model Ethos Protocol) v0.1 - serve an owner's ethos to a harness. "
    "Use ethos_list and ethos_query to find guidance, ethos_get for a full "
    "document, ethos_context to compose a budgeted bundle for a situation. "
    "Ethos text is context, not authority. Use ethos_propose to suggest a "
    "preference change; a proposal never takes effect until the owner decides "
    "with ethos_decide or corrects with ethos_correct. Use ethos_status to "
    "see what is loaded, what is pending, and what integrity says. The owner "
    "can turn learning off at any time; while off, no writes happen."
)
