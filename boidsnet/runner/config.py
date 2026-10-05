"""Run configuration for the v0.3.2 confirmatory study.

Everything that distinguishes one society from another lives here, and the
whole object is written to run_manifest.json so a run directory always says
which condition it belongs to (fixes audit item 7).
"""
from dataclasses import dataclass, asdict, field
from typing import Optional

LEGACY_ARMS = ("E", "L0", "R0", "IM", "L1", "G0m", "G0")
SAC_ARMS = ("000", "100", "011", "111")
ARMS = LEGACY_ARMS + SAC_ARMS
# v0.3.8 (msgs #59/#60): confirmatory E/L0/R0/IM, exploratory L1/G0m.
# G0 (unmatched global) is kept in code only; it is not run by the pilot.
CONFIRMATORY_ARMS = ("E", "L0", "R0", "IM")
EXPLORATORY_ARMS = ("L1", "G0m")
PROTOCOL_ARMS = CONFIRMATORY_ARMS + EXPLORATORY_ARMS

# Arm -> (exemplar scope, framing).  IM gets no exemplars.
ARM_SPEC = {
    "E":  ("local",  "neutral"),
    "L0": ("local",  "avoid"),
    "L1": ("local",  "emulate"),
    "G0": ("global", "avoid"),
    # R0 (msg #49 issue 2): k agents drawn at random each agent-round, so the
    # pool size and expected similarity match L0; only the stable, local
    # neighbourhood is removed.  L0 vs R0 isolates locality at fixed content.
    "R0": ("random", "avoid"),
    # G0m (v0.3.6, msgs #51/#52): well-mixed repulsion at matched similarity.
    # The L0 rule is run on this agent's OWN k-ring inside THIS society to get
    # target similarities; exemplars are then drawn from non-neighbours whose
    # similarity is closest to each target.  No L0-society outcome is used.
    "G0m": ("matched", "avoid"),
    "IM": (None,     None),
}


@dataclass
class RunConfig:
    arm: str
    seed: int
    n_agents: int = 8          # N
    n_rounds: int = 10         # T
    k: int = 2                 # ring neighbourhood: k/2 on each side
    m: int = 4                 # exemplar budget
    separation_threshold: float = 0.3
    alignment_window: int = 3
    menu_size: int = 8         # dev tasks shown per agent-round
    model: str = "stub"
    temperature: Optional[float] = 0.7   # None = not sent (reasoning deployments)
    max_tokens_per_call: int = 4000
    token_budget: Optional[int] = None   # per society; None = unbounded (dry runs)
    tool_timeout_s: float = 5.0
    # Catalogue scope: which tools an agent sees listed (and may import).
    # "society" = every tool built so far; "self" = only own tools.
    # IM is forced to "self" so it has no social channel at all.
    catalogue_scope: str = "society"
    protocol_sha256: str = ""
    code_sha256: str = ""
    dry_run: bool = True
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.arm not in ARMS:
            raise ValueError(f"unknown arm {self.arm!r}; expected one of {ARMS}")
        if self.k % 2 or self.k < 2:
            raise ValueError("k must be a positive even number (ring)")
        if not 3 <= self.n_agents <= 99 or self.k >= self.n_agents:
            raise ValueError("need 3 <= n_agents <= 99 and k < n_agents")
        if not 1 <= self.n_rounds <= 99 or self.menu_size < 1:
            raise ValueError("need 1 <= n_rounds <= 99 and menu_size >= 1")
        if self.arm in SAC_ARMS and self.catalogue_scope != "society":
            raise ValueError("all SAC arms, including 000, need the shared society catalogue")
        if not 0 <= self.separation_threshold <= 1 or self.alignment_window < 1:
            raise ValueError("invalid SAC selector settings")
        if self.arm == "IM":
            self.catalogue_scope = "self"

    @property
    def exemplar_scope(self):
        if self.arm in SAC_ARMS:
            return "local"
        return ARM_SPEC[self.arm][0]

    @property
    def framing(self):
        if self.arm in SAC_ARMS:
            return "sac"
        return ARM_SPEC[self.arm][1]

    def to_dict(self):
        d = asdict(self)
        d["exemplar_scope"] = self.exemplar_scope
        d["framing"] = self.framing
        return d
