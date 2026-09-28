"""CDC 2.11.2 lane runtime lifecycle primitives.

The runtime models safe lifecycle transitions. Durable CAS, process evidence
and Git effects are supplied by the caller and are never inferred here.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LaneState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    HANDOFF_PENDING = "handoff_pending"
    RELEASED = "released"
    STALE = "stale"


@dataclass
class LaneRuntime:
    lane_id: str
    generation: int
    state: LaneState = LaneState.QUEUED
    last_activity_ref: Optional[str] = None
    pending_effects: bool = False

    def heartbeat(self, activity_ref: str) -> None:
        if not activity_ref or activity_ref == self.last_activity_ref:
            raise ValueError("heartbeat requires a new activity reference")
        self.last_activity_ref = activity_ref
        self.state = LaneState.RUNNING

    def request_handoff(self) -> None:
        if self.state != LaneState.RUNNING:
            raise ValueError("only active lanes can handoff")
        self.state = LaneState.HANDOFF_PENDING

    def release(self) -> None:
        if self.pending_effects:
            raise ValueError("lane release requires drained effects")
        if self.state not in (LaneState.HANDOFF_PENDING, LaneState.RUNNING):
            raise ValueError("lane is not releasable")
        self.state = LaneState.RELEASED
