# Reference-only prototype. NOT MEP code, NOT shipped, NOT part of the
# stdlib-only promise. Captured 2026-11-14 from the owner's session with
# another assistant ("Gemini"). Preserved verbatim apart from a single
# import-order fix. It targets the weight-space marketplace track, which is
# parked in docs/research/2026-11-14-*.md. Do not import this from mep/.
# Provenance: see docs/research/2026-11-14-compositor-prototype.md.

import hashlib
from dataclasses import dataclass, field
import numpy as np


@dataclass
class TastePacket:
  creator_id: str
  public_key: str
  U: np.ndarray  # (d_out, r) left singular vectors
  S: np.ndarray  # (r,) singular values
  V: np.ndarray  # (d_in, r) right singular vectors
  watermark_eps: float = 1e-3
  lineage: list = field(default_factory=list)

  @property
  def delta_w(self) -> np.ndarray:
    """Reconstructs the dense perturbation matrix."""
    return (self.U * self.S) @ self.V.T

  @property
  def packet_hash(self) -> str:
    """Cryptographic commitment of the taste payload."""
    h = hashlib.sha256()
    h.update(self.creator_id.encode())
    h.update(self.U.tobytes())
    h.update(self.S.tobytes())
    h.update(self.V.tobytes())
    return h.hexdigest()[:16]


def _derive_carrier_basis(
    public_key: str, dim: int, rank: int, P_null: np.ndarray
) -> np.ndarray:
  """Generates a deterministic, orthonormal carrier basis strictly inside Null(K0)."""
  seed = int.from_bytes(
      hashlib.sha256(public_key.encode()).digest()[:8], 'big'
  )
  rng = np.random.default_rng(seed)
  raw_carriers = rng.standard_normal((dim, rank))
  # Project carriers into the safe null space so watermarks never leak into K0
  safe_carriers = P_null @ raw_carriers
  Q, _ = np.linalg.qr(safe_carriers)
  return Q[:, :rank]


def mint_taste_packet(
    creator_id: str,
    public_key: str,
    raw_delta: np.ndarray,
    P_null: np.ndarray,
    rank: int = 4,
    eps: float = 1e-3,
) -> TastePacket:
  """Projects a raw taste perturbation into Null(K0), embeds a keyed subspace

  watermark, and factorizes into a compact low-rank packet.
  """
  # 1. Enforce AlphaEdit null-space invariance (K0 @ delta_safe == 0)
  delta_safe = raw_delta @ P_null

  # 2. Truncated SVD to extract principal taste modes
  U, S, Vt = np.linalg.svd(delta_safe, full_matrices=False)
  U_r, S_r, V_r = U[:, :rank], S[:rank], Vt[:rank, :].T

  # 3. Embed invisible geometric watermark into left singular vectors
  C = _derive_carrier_basis(
      public_key, U_r.shape[0], rank, np.eye(U_r.shape[0])
  )
  U_watermarked = U_r + eps * C
  # Re-orthonormalize U_watermarked while preserving carrier alignment
  U_watermarked, _ = np.linalg.qr(U_watermarked)

  pkt = TastePacket(
      creator_id=creator_id,
      public_key=public_key,
      U=U_watermarked,
      S=S_r,
      V=V_r,
      watermark_eps=eps,
  )
  pkt.lineage.append({'root': pkt.packet_hash, 'weight': 1.0})
  return pkt


def weave_and_attribute(
    base_profile: TastePacket | None,
    market_packets: list[tuple[TastePacket, float]],  # (packet, blend_strength)
    P_null: np.ndarray,
    max_spectral_norm: float = 0.5,
) -> tuple[TastePacket, dict[str, float]]:
  """Weaves marketplace taste packets onto a user's base profile without

  overwriting existing style, and computes exact Frobenius energy royalties.
  """
  d_out, d_in = market_packets[0][0].U.shape[0], market_packets[0][0].V.shape[0]
  W_comp = np.zeros((d_out, d_in))

  # Build personal invariance projector so new traits expand rather than overwrite
  if base_profile is not None:
    W_comp += base_profile.delta_w
    V_self = base_profile.V
    P_self = np.eye(d_in) - (V_self @ V_self.T)
  else:
    P_self = np.eye(d_in)

  # 1. Orthogonalized Weaving
  for pkt, beta in market_packets:
    # Restrict incoming taste to the orthogonal complement of K0 AND existing taste
    delta_orthogonal = (pkt.delta_w @ P_null) @ P_self
    W_comp += beta * delta_orthogonal

  # 2. Spectral Norm Clamping (prevents activation blowup across sequential weaves)
  U, S, Vt = np.linalg.svd(W_comp, full_matrices=False)
  if S[0] > max_spectral_norm:
    S = S * (max_spectral_norm / S[0])
  W_bounded = (U * S) @ Vt

  # 3. Spectral Royalty / Frobenius Energy Attribution
  # Measure how much energy of the final woven matrix projects onto each creator's subspace
  energies = {}
  all_sources = ([base_profile] if base_profile else []) + [
      p for p, _ in market_packets
  ]

  for src in all_sources:
    # Project composite matrix onto creator's orthonormal right-singular basis V_i
    projected_energy = np.linalg.norm(W_bounded @ src.V, ord='fro') ** 2
    energies[src.creator_id] = energies.get(src.creator_id, 0.0) + float(
        projected_energy
    )

  total_energy = sum(energies.values()) + 1e-12
  royalty_shares = {
      cid: round(e / total_energy, 4) for cid, e in energies.items()
  }

  # Package resulting composite profile
  rank = min(16, len(S))
  woven_pkt = TastePacket(
      creator_id='composite_user',
      public_key='user_pk',
      U=U[:, :rank],
      S=S[:rank],
      V=Vt[:rank, :].T,
      lineage=[
          {'source': p.packet_hash, 'share': royalty_shares[p.creator_id]}
          for p in all_sources
      ],
  )
  return woven_pkt, royalty_shares


# --- Quick Verification Run ---
if __name__ == '__main__':
  rng = np.random.default_rng(42)
  d_model = 128

  # Simulate K0 (preserved core knowledge subspace of rank 32)
  K0 = rng.standard_normal((32, d_model))
  _, _, Vt_k0 = np.linalg.svd(K0, full_matrices=False)
  P_null = np.eye(d_model) - (Vt_k0.T @ Vt_k0)

  # Mint two creator taste packets
  alice = mint_taste_packet(
      'alice_brutalism',
      'pk_alice',
      rng.standard_normal((d_model, d_model)),
      P_null,
  )
  bob = mint_taste_packet(
      'bob_lyrical', 'pk_bob', rng.standard_normal((d_model, d_model)), P_null
  )

  # Weave 70% Alice + 40% Bob
  composite, shares = weave_and_attribute(
      None, [(alice, 0.7), (bob, 0.4)], P_null
  )

  # Verify mathematical guarantees
  k0_leakage = np.linalg.norm(K0 @ composite.delta_w)
  print(f'K0 Invariance Leakage (should be ~0): {k0_leakage:.2e}')
  print(f'Verified Royalty Attribution Shares:  {shares}')
