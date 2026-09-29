#!/usr/bin/env python3
"""Check tracked Python placement before candidate imports or release claims."""
import argparse
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = ('bootstrap/', 'src/cdc27/', 'src/continuous-development-cycle/')
TEST_ROOTS = ('bootstrap/tests/', 'src/continuous-development-cycle/tests/')
REGULAR_MODES = {'100644', '100755'}


def validate(root):
    try:
        entries = subprocess.check_output(
            ['git', '-C', str(root), 'ls-files', '--stage', '-z'], text=True).split('\0')
    except subprocess.CalledProcessError as exc:
        raise ValueError('cannot inspect tracked repository paths') from exc
    errors = []
    tracked = {}
    for entry in filter(None, entries):
        metadata, name = entry.split('\t', 1)
        mode, _, stage = metadata.split()
        tracked[name] = mode
        if stage != '0':
            errors.append(f'{name}: unresolved Git index entry')
    for name in sorted(tracked):
        path = PurePosixPath(name)
        if path.suffix != '.py':
            continue
        if tracked[name] not in REGULAR_MODES:
            errors.append(f'{name}: Python source must be a tracked regular file')
        if not name.startswith(SOURCE_ROOTS):
            errors.append(f'{name}: Python code outside canonical source roots')
        if not path.name.startswith('test'):
            continue
        # Match Python 3.12 unittest.loader's test-module filename rule.
        if not re.fullmatch(r'[_a-z]\w*\.py', path.name, re.IGNORECASE):
            errors.append(f'{name}: filename is skipped by unittest discovery')
        test_root = next((prefix for prefix in TEST_ROOTS if name.startswith(prefix)), None)
        if test_root is None:
            errors.append(f'{name}: outside the test roots executed by release validation')
            continue
        parent = path.parent
        while str(parent) + '/' != test_root:
            marker = str(parent / '__init__.py')
            if tracked.get(marker) not in REGULAR_MODES:
                errors.append(f'{name}: unittest discovery requires tracked regular file {marker}')
            parent = parent.parent
    if errors:
        raise ValueError('\n'.join(errors))
    return len(tracked)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        count = validate(args.root)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'LAYOUT_RED: {exc}')
        return 1
    print(f'LAYOUT_GREEN: {count} tracked paths inspected')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
