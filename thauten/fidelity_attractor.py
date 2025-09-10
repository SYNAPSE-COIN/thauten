import logging
import random
from typing import List, Literal

from pydantic import Field

from errloom import Span
from errloom.attractor import Attractor
from errloom.comm import CommModel
from errloom.synapse import Synapse


class FidelityCritique(CommModel):
    """
    Structured record for a fidelity check, contrasting an original passage
    with its reconstructed (decompressed) version.
    """

    deviations: List[str] = Field(default=[], description="Factual shifts or alterations relative to the source.")
    inaccuracies: List[str] = Field(default=[], description="Incorrect claims introduced during reconstruction.")
    missing_statements: List[str] = Field(default=[], description="Important details from the source that were omitted.")
    acceptable_extensions: List[str] = Field(default=[], description="Valid elaborations that do not contradict the source.")
    severity: Literal["MINOR", "MODERATE", "MAJOR"] = Field(description="Overall seriousness of detected issues.")
    quality: Literal["EXCELLENT", "GOOD", "FAIR", "POOR"] = Field(description="Overall reconstruction quality.")

    def __synapse__(self, core: Synapse, span: Span) -> str:
        """Special hook for synapseware to inject content. Returns a compact schema."""
        return self.get_compact_schema(include_descriptions=True)

    @property
    def total_issues(self) -> int:
        """Total count of detected problems."""
        return len(self.deviations) + len(self.inaccuracies) + len(self.missing_statements)


class FidelityAttractor(Attractor):
    def __init__(self, a, b, alpha=0.01, beta=1.0):
        super().__init__()
        self.a = a
        self.b = b
        self.alpha = alpha
        self.beta = beta

        # tb.add_row("Alpha (compression)", f"{alpha}")
        # tb.add_row("Beta (fidelity)", f"{beta}")

        self.add_rule(self.rule_fidelity)

    def rule_fidelity(self, rollout):
        n_tokens = len(self.a.split())
        fidelity = random.uniform(0, 5)

        decel = self.alpha * n_tokens + self.beta * (1 - fidelity)
        gravity = 1 - decel
        gravity = max(0.0, gravity)

        return gravity
