"""CDC 2.11.2 cooperative project lane model.

This module provides the portable claim contract. Durable persistence, CAS,
Git effects and host fencing remain outside this contract and must be supplied
by the runtime adapter.
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
    executor_id: str = "unknown"
    role: str = "worker"

    def normalized_writes(self) -> FrozenSet[str]:
        return frozenset(normalize_path(p) for p in self.write_paths)

    @property
    def is_writer(self) -> bool:
        return bool(self.write_paths) or self.kind == LaneKind.INTEGRATOR


def normalize_path(path: str) -> str:
    """Normalize portable paths for overlap comparison.

    Portable lane ownership treats equivalent Unicode spellings, path
    separators and case variants as the same scope. It is intentionally a
    comparison rule, not an OS-level filesystem fence.
    """
    value = unicodedata.normalize("NFC", path).replace("\\", "/")
    value = value.casefold()
    return str(PurePosixPath(value))


def paths_overlap(left: LaneClaim, right: LaneClaim) -> bool:
    """Return whether two claims may mutate the same portable scope."""
    for a in left.normalized_writes():
        for b in right.normalized_writes():
            pa = PurePosixPath(a)
            pb = PurePosixPath(b)
            if pa == pb or pa in pb.parents or pb in pa.parents:
                return True
    return False


def admit_writer(existing: list[LaneClaim], candidate: LaneClaim) -> bool:
    """Apply lane admission before any writer effect occurs."""
    if not candidate.is_writer:
        return True
    if candidate.kind == LaneKind.INTEGRATOR:
        return not any(e.kind == LaneKind.INTEGRATOR for e in existing)
    if any(e.kind == LaneKind.INTEGRATOR for e in existing):
        return False
    return not any(paths_overlap(e, candidate) for e in existing if e.is_writer)
