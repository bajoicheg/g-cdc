"""One hosted packet runner. Never execute on the VPS. No provider/CI submission."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent
KIT=ROOT.parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--sdk-source',type=Path,required=True,help='credential-free exact pinned SDK source export')
    parser.add_argument('--receipts',type=Path,required=True,help='new directory, outside source')
    args=parser.parse_args()
    freeze=json.loads((KIT/'freeze.json').read_text())
    for name,expected in freeze['files'].items():
        if digest(KIT/name)!=expected:raise ValueError('packet freeze mismatch: '+name)
    pins=json.loads((ROOT/'sdk-source-pins.json').read_text())['files']
    for name,expected in pins.items():
        if digest(args.sdk_source/name)!=expected:raise ValueError('SDK source mismatch: '+name)
    args.receipts.mkdir(parents=True,exist_ok=False)
    outcomes=[]; deadline=time.monotonic()+600
    with tempfile.TemporaryDirectory(prefix='cdc-admission-hosted-') as temp:
        work=Path(temp);sdk=work/'sdk'; sdk.mkdir()
        for name in pins:
            dest=sdk/name;dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(args.sdk_source/name,dest)
        # Same frozen SDK tests, only this module changes in candidate overlay.
        shutil.copyfile(ROOT/'candidate/immutable_history_cache.py',sdk/'scripts/immutable_history_cache.py')
        package=work/'operator/cdc_operator';package.mkdir(parents=True)
        (package/'__init__.py').write_text('')
        for name in ('session.py','ownership.py','handover.py'):
            shutil.copyfile(ROOT/'baseline'/name,package/name)
        shutil.copyfile(ROOT/'candidate/quota.py',package/'quota.py')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=os.pathsep.join([
            str(package.parent),str(ROOT/'tests'),str(sdk/'scripts'),str(sdk/'tests')]),
            GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_NAME='Hosted fixture',
            GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_NAME='Hosted fixture',
            GIT_COMMITTER_EMAIL='fixture@example.invalid')
        def run(label,argv,variant,expected,marker=None):
            stdout=args.receipts/(label+'.stdout');stderr=args.receipts/(label+'.stderr')
            with stdout.open('xb') as out,stderr.open('xb') as err:
                timed_out=False; exit_code=None
                try:
                    remaining=deadline-time.monotonic()
                    if remaining<=0:raise subprocess.TimeoutExpired(argv,0)
                    result=subprocess.run(argv,cwd=work,env=dict(env,ADMISSION_VARIANT=variant),
                                          stdout=out,stderr=err,timeout=remaining)
                    exit_code=result.returncode
                except subprocess.TimeoutExpired:
                    timed_out=True
            receipt={'label':label,'argv':argv,'variant':variant,'exit':exit_code,'timed_out':timed_out,
                     'stdout_sha256':digest(stdout),'stderr_sha256':digest(stderr),
                     'stdout':stdout.name,'stderr':stderr.name}
            # Persist actual return before interpreting RED/GREEN.
            (args.receipts/(label+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
            passed=not timed_out and exit_code==expected
            if marker:
                text=stderr.read_text();passed=passed and marker in text and 'FAILED (failures=1)' in text and 'ERROR:' not in text
            receipt['meets_expectation']=passed;outcomes.append(receipt)
        python=[sys.executable,'-B','-m','unittest','-v']
        run('old-cache-red',python+['test_admission.OldExpectedRed.test_oversized_cache_does_not_materialize_snapshot'],
            'baseline',1,'eager full snapshot serialization')
        run('old-quota-red',python+['test_admission.OldExpectedRed.test_recorded_correction_is_conservative'],
            'baseline',1,'bounded conservative correction denied')
        run('candidate-packet-green',python+['test_admission'],'candidate',0)
        run('candidate-native-history-green',python+['test_history_reuse','test_native_unknown_recovery','test_project_budget_store','test_sdk_boundary'],
            'candidate',0)
        run('preserved-maintenance-green',[sys.executable,'-B','-m','unittest','discover','-s',str(KIT),
                                          '-p','test_maintenance.py','-v'],'candidate',0)
    success=all(r['meets_expectation'] for r in outcomes)
    (args.receipts/'result.json').write_text(json.dumps({'passed':success,'runs':outcomes,
        'freeze_sha256':digest(KIT/'freeze.json'),'installation':False,'actual_kimi_exercise':False},indent=2)+'\n')
    return 0 if success else 1
if __name__=='__main__':sys.exit(main())
