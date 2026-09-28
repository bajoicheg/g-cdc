from scripts.project_lanes import (
    LaneClaim,
    LaneKind,
    admit_writer,
    paths_overlap,
)
from scripts.project_lane_runtime import LaneRuntime, LaneState


def claim(name, writes, kind=LaneKind.WORKER):
    return LaneClaim(
        lane_id=name,
        invocation_id=name,
        kind=kind,
        source_head="head",
        worktree=name,
        branch=name,
        write_paths=frozenset(writes),
    )


def test_disjoint_writers_can_coexist():
    assert admit_writer([claim("a", {"src/a"})], claim("b", {"src/b"}))


def test_parent_child_paths_overlap():
    assert paths_overlap(claim("a", {"src"}), claim("b", {"src/a"}))
    assert not admit_writer([claim("a", {"src"})], claim("b", {"src/a"}))


def test_portable_case_and_separator_variants_overlap():
    assert paths_overlap(claim("a", {"SRC\\Feature"}), claim("b", {"src/feature"}))


def test_read_only_lane_does_not_block_writer():
    assert admit_writer([claim("review", set(), LaneKind.REVIEW)], claim("worker", {"src/a"}))


def test_integrator_is_singleton():
    existing = claim("i1", set(), LaneKind.INTEGRATOR)
    candidate = claim("i2", set(), LaneKind.INTEGRATOR)
    assert not admit_writer([existing], candidate)


def test_runtime_requires_fresh_heartbeat_and_drained_effects():
    runtime = LaneRuntime("lane", 1)
    runtime.heartbeat("activity-1")
    assert runtime.state == LaneState.RUNNING
    runtime.pending_effects = True
    try:
        runtime.release()
    except ValueError:
        pass
    else:
        raise AssertionError("release accepted pending effects")
