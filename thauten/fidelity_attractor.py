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

