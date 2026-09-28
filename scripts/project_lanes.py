"""CDC 2.11.2 cooperative project lane model.

This module provides the durable contract layer for foreground, watchdog,
worker and review lanes. Persistence/adapters are intentionally injected;
this module does not pretend to own Git hosting or OS fencing.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath
import unicodedata
from typing import FrozenSet


class LaneKind(str, Enum):
    FOREGROUND = "foreground"
    WATCHDOG = "watchdog"
    WORKER = "worker"
    REVIEW = "review"
    INTEGRATOR = "integrator"


@dataclass(frozen=True)
class LaneClaim:
    lane_id: str
    invocation_id: str
    kind: LaneKind
    source_head: str
    worktree: str
    branch: str
    read_paths: FrozenSet[str] = field(default_factory=frozenset)
    write_paths: FrozenSet[str] = field(default_factory=frozenset)

    def normalized_writes(self) -> FrozenSet[str]:
        return frozenset(normalize_path(p) for p in self.write_paths)


def normalize_path(path: str) -> str:
    """Normalize portable paths for overlap comparison."""
    value = unicodedata.normalize("NFC", path).replace("\\", "/")
    return str(PurePosixPath(value))


def paths_overlap(left: LaneClaim, right: LaneClaim) -> bool:
    """Return whether two writer claims may mutate the same portable scope."""
    for a in left.normalized_writes():
        for b in right.normalized_writes():
            pa = PurePosixPath(a)
            pb = PurePosixPath(b)
            if pa == pb or pa in pb.parents or pb in pa.parents:
                return True
    return False


def admit_writer(existing: list[LaneClaim], candidate: LaneClaim) -> bool:
    """Admission rule: conflicting writers serialize before effects."""
    if candidate.kind == LaneKind.INTEGRATOR:
        return all(e.kind != LaneKind.INTEGRATOR for e in existing)
    return not any(paths_overlap(e, candidate) for e in existing)
