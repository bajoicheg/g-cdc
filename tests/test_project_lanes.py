from scripts.project_lanes import (
    LaneClaim,
    LaneKind,
    admit_writer,
    paths_overlap,
)


def claim(name, writes):
    return LaneClaim(
        lane_id=name,
        invocation_id=name,
        kind=LaneKind.WORKER,
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


def test_integrator_is_singleton():
    existing = LaneClaim(
        lane_id="i1",
        invocation_id="i1",
        kind=LaneKind.INTEGRATOR,
        source_head="head",
        worktree="i1",
        branch="main",
    )
    candidate = LaneClaim(
        lane_id="i2",
        invocation_id="i2",
        kind=LaneKind.INTEGRATOR,
        source_head="head",
        worktree="i2",
        branch="main",
    )
    assert not admit_writer([existing], candidate)
