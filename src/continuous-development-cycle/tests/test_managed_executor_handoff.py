import copy,hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import managed_executor_handoff as m

def direct(base,commit):
 return {
  "schema":"managed-executor-handoff/v1","pool_id":"p","change_id":"c","task_id":"t",
  "attempt_id":"a1","parent_invocation_id":"parent","executor_id":"exec",
  "base_sha":base,"assigned_branch":"worker-a","transport":"direct_branch",
  "source_result_commit":commit,"direct_result_commit":commit,"artifact_ref":None,
  "changed_paths":["src/a.txt"],"evidence_refs":["tests:green"]}

class T(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.repo=Path(self.tmp.name)
  def git(*args): return subprocess.check_output(["git","-C",str(self.repo),*args],text=True).strip()
  git("init","-q");git("config","user.email","cdc@example.invalid");git("config","user.name","CDC")
  (self.repo/"seed").write_text("base");git("add","seed");git("commit","-q","-m","base")
  self.base=git("rev-parse","HEAD")
  git("switch","-q","-c","worker-a")
  (self.repo/"src").mkdir();(self.repo/"src"/"a.txt").write_text("a")
  git("add","src/a.txt");git("commit","-q","-m","result");self.result=git("rev-parse","HEAD")

 def tearDown(self): self.tmp.cleanup()

 def proof(self,h,commit=None,changed=None):
  return {
   "schema":"managed-executor-publication-proof/v1",
   "handoff_ref":m.canonical_handoff_ref(h),"pool_id":h["pool_id"],"task_id":h["task_id"],
   "attempt_id":h["attempt_id"],"base_sha":h["base_sha"],"assigned_branch":h["assigned_branch"],
   "published_commit":commit or self.result,"observed_changed_paths":changed or list(h["changed_paths"]),
   "evidence_refs":["git:remote-head","tests:remote-green"],"result_verified":True,
   "authorizes_product_write":False,"authorizes_shared_branch_write":False,
   "authorizes_force_push":False,"authorizes_merge":False,"authorizes_release":False,
   "authorizes_scope_expansion":False,"authorizes_scheduler_mutation":False}

 def test_direct_branch_plan_never_requires_reexecution_or_grants_authority(self):
  h=direct(self.base,self.result);p=m.publication_plan(h)
  self.assertEqual(p["action"],"VERIFY_DIRECT_ASSIGNED_BRANCH");self.assertFalse(p["requires_reexecution"])
  for name in m.AUTHORITY_FIELDS:self.assertFalse(p[name])

 def test_direct_publication_proof_live_verifies_exact_branch_and_ancestry(self):
  h=direct(self.base,self.result)
  self.assertTrue(m.validate_publication_proof(self.proof(h),h,self.repo)["result_verified"])

 def test_direct_result_must_match_exact_branch_head(self):
  h=direct(self.base,self.result);p=self.proof(h,commit=self.base)
  with self.assertRaisesRegex(ValueError,"direct publication commit mismatch"):m.validate_publication_proof(p,h,self.repo)

 def test_content_artifact_digest_is_authenticated_and_no_rerun(self):
  artifact=self.repo/"result.patch";artifact.write_bytes(b"patch-bytes")
  h=direct(self.base,self.result);h.update(transport="content_artifact",source_result_commit=None,direct_result_commit=None,
   artifact_ref={"path":"result.patch","sha256":"sha256:"+hashlib.sha256(b"patch-bytes").hexdigest(),"format":"unified_diff"})
  p=m.publication_plan(h,self.repo)
  self.assertEqual(p["action"],"IMPORT_CONTENT_ARTIFACT_TO_ASSIGNED_BRANCH");self.assertFalse(p["requires_reexecution"])

 def test_content_artifact_digest_mismatch_fails_closed(self):
  (self.repo/"result.patch").write_bytes(b"actual")
  h=direct(self.base,self.result);h.update(transport="content_artifact",source_result_commit=None,direct_result_commit=None,
   artifact_ref={"path":"result.patch","sha256":"sha256:"+"0"*64,"format":"unified_diff"})
  with self.assertRaisesRegex(ValueError,"digest mismatch"):m.publication_plan(h,self.repo)

 def test_artifact_path_cannot_escape_evidence_root(self):
  h=direct(self.base,self.result);h.update(transport="content_artifact",source_result_commit=None,direct_result_commit=None,
   artifact_ref={"path":"../escape.patch","sha256":"sha256:"+"0"*64,"format":"unified_diff"})
  with self.assertRaises(ValueError):m.validate_handoff(h)

 def test_publication_proof_binds_handoff_digest(self):
  h=direct(self.base,self.result);p=self.proof(h);p["handoff_ref"]="sha256:"+"0"*64
  with self.assertRaisesRegex(ValueError,"handoff_ref mismatch"):m.validate_publication_proof(p,h,self.repo)

 def test_changed_path_manifest_is_portable_and_exact(self):
  h=direct(self.base,self.result);h["changed_paths"]=["src/Foo"]
  p=self.proof(h,changed=["src/foo"])
  self.assertTrue(m.validate_publication_proof(p,h,self.repo))
  p=self.proof(h,changed=["src/bar"])
  with self.assertRaisesRegex(ValueError,"changed paths"):m.validate_publication_proof(p,h,self.repo)

 def test_git_bundle_transport_preserves_source_commit_identity(self):
  bundle=self.repo/"result.bundle";subprocess.check_call(["git","-C",str(self.repo),"bundle","create",str(bundle),"worker-a"],stdout=subprocess.DEVNULL)
  h=direct(self.base,self.result);h.update(transport="content_artifact",direct_result_commit=None,
   artifact_ref={"path":"result.bundle","sha256":"sha256:"+hashlib.sha256(bundle.read_bytes()).hexdigest(),"format":"git_bundle"})
  m.publication_plan(h,self.repo)
  p=self.proof(h)
  self.assertTrue(m.validate_publication_proof(p,h,self.repo))
  p["published_commit"]=self.base
  with self.assertRaisesRegex(ValueError,"preserve source result commit"):m.validate_publication_proof(p,h,self.repo)

 def test_authority_escalation_in_proof_is_rejected(self):
  h=direct(self.base,self.result);p=self.proof(h);p["authorizes_merge"]=True
  with self.assertRaisesRegex(ValueError,"must remain false"):m.validate_publication_proof(p,h,self.repo)

if __name__=="__main__":unittest.main()
