# Honest variant of the bundled verification. The bundled run checks
# ||K0 @ composite.delta_w||, which is not the invariant the construction
# builds. The construction projects the INPUT side of the perturbation into
# the orthogonal complement of the preserved keys, so the guarantee is
# ||composite.delta_w @ K0.T||_F ~ 0 (no component of any preserved key
# direction survives the woven edit). This script measures both.
import numpy as np
import sys
sys.path.insert(0, ".")
from importlib import import_module

mod = import_module("2026-11-14-taste-compositor" if False else "taste_compositor_20261114") if False else None

# Load the prototype by path since the filename is not a valid module name.
import importlib.util
spec = importlib.util.spec_from_file_location(
    "taste_compositor", "docs/research/prototypes/2026-11-14-taste-compositor.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

rng = np.random.default_rng(42)
d_model = 128
K0 = rng.standard_normal((32, d_model))
_, _, Vt_k0 = np.linalg.svd(K0, full_matrices=False)
P_null = np.eye(d_model) - (Vt_k0.T @ Vt_k0)

alice = mod.mint_taste_packet('alice_brutalism', 'pk_alice', rng.standard_normal((d_model, d_model)), P_null)
bob = mod.mint_taste_packet('bob_lyrical', 'pk_bob', rng.standard_normal((d_model, d_model)), P_null)
composite, shares = mod.weave_and_attribute(None, [(alice, 0.7), (bob, 0.4)], P_null)

print(f"bundled check   ||K0 @ dW||   = {np.linalg.norm(K0 @ composite.delta_w):.3e}")
print(f"correct check   ||dW @ K0.T|| = {np.linalg.norm(composite.delta_w @ K0.T):.3e}")
print(f"mint leakage alice              = {np.linalg.norm(alice.delta_w @ K0.T):.3e}")
print(f"mint leakage bob                = {np.linalg.norm(bob.delta_w @ K0.T):.3e}")
print(f"shares                          = {shares}")
