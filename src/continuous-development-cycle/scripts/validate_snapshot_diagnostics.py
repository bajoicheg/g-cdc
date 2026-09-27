import json
import pathlib
import sys


def validate_snapshot(consumer, expected_version, expected_tree):
    source = pathlib.Path("consumer/evidence") / consumer / "source.json"
    data = json.loads(source.read_text())

    checks = [
        ("candidate_version", expected_version, data.get("candidate_version")),
        ("candidate_package_tree", expected_tree, data.get("candidate_package_tree")),
    ]

    for field, expected, actual in checks:
        if actual != expected:
            raise RuntimeError(
                f"snapshot validation failed consumer={consumer} "
                f"field={field} expected={expected} actual={actual}"
            )

    commit = data.get("source_commit", "")
    if len(commit) != 40:
        raise RuntimeError(
            f"snapshot validation failed consumer={consumer} "
            f"field=source_commit expected_length=40 actual={commit}"
        )


if __name__ == "__main__":
    validate_snapshot(sys.argv[1], sys.argv[2], sys.argv[3])
