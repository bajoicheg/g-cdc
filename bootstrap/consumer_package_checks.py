#!/usr/bin/env python3
"""Run packaged regressions in a clean consumer layout, without canonical siblings."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

def run(package_root):
    package=Path(package_root).resolve()
    if not (package/'tests').is_dir():raise ValueError('package test directory is absent')
    if any(p.is_symlink() for p in package.rglob('*')):
        raise ValueError('clean consumer package requires self-contained regular paths')
    with tempfile.TemporaryDirectory(prefix='cdc-clean-consumer-') as directory:
        root=Path(directory)
        target=root/'.agents'/'skills'/'continuous-development-cycle'
        shutil.copytree(package,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        result=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(target/'tests'),'-v'],cwd=root,capture_output=True,text=True)
        print(result.stdout+result.stderr,end='')
        print('CONSUMER_PACKAGE_GREEN' if result.returncode==0 else 'CONSUMER_PACKAGE_RED')
        return result.returncode

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root',default=str(Path(__file__).resolve().parents[1]/'src/continuous-development-cycle'))
    args=parser.parse_args(argv)
    try:return run(args.package_root)
    except (OSError,ValueError) as exc:
        print('CONSUMER_PACKAGE_RED:',exc,file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
