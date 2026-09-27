import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import managed_executor_handoff as m

class T(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.repo=self.root/"work";self.remote=self.root/"remote.git";self.alt=self.root/"alt.git"
  self.repo.mkdir()
  subprocess.check_call(["git","init","--bare","-q",str(self.remote)])
  subprocess.check_call(["git","init","--bare","-q",str(self.alt)])
  def git(*args):return subprocess.check_output(["git","-C",str(self.repo),*args],text=True).strip()
  self.git=git
  git("init","-q");git("config","user.email","cdc@example.invalid");git("config","user.name","CDC")
  (self.repo/"seed").write_text("base");git("add","seed");git("commit","-q","-m","base")
  self.base=git("rev-parse","HEAD")
  git("switch","-q","-c","worker-a")
  (self.repo/"src").mkdir();(self.repo/"src"/"a.txt").write_text("a")
  git("add","src/a.txt");git("commit","-q","-m","result");self.result=git("rev-parse","HEAD")
  git("remote","add","origin",str(self.remote));git("remote","add","alt",str(self.alt))
  self.push("origin","worker-a")
  self.repository="example/repository"
  self.remote_id=m.publication_remote_identity(self.repo,"origin")

 def tearDown(self):self.tmp.cleanup()

 def push(self,remote,source,target="refs/heads/worker-a"):
  subprocess.check_call(["git","-C",str(self.repo),"push","-q","--force",remote,f"{source}:{target}"])

 def direct(self,commit=None):
  commit=commit or self.result
  return {
   "schema":"managed-executor-handoff/v1","pool_id":"p","change_id":"c","task_id":"t",
   "attempt_id":"a1","parent_invocation_id":"parent","executor_id":"exec",
   "base_sha":self.base,"assigned_branch":"worker-a",
   "publication_repository":self.repository,"publication_remote_id":self.remote_id,
   "transport":"direct_branch","source_result_commit":commit,"direct_result_commit":commit,
   "artifact_ref":None,"changed_paths":["src/a.txt"],"evidence_refs":["tests:green"]}

 def proof(self,h,commit=None,changed=None):
  return {
   "schema":"managed-executor-publication-proof/v1",
   "handoff_ref":m.canonical_handoff_ref(h),"pool_id":h["pool_id"],"task_id":h["task_id"],
   "attempt_id":h["attempt_id"],"base_sha":h["base_sha"],"assigned_branch":h["assigned_branch"],
   "publication_repository":h["publication_repository"],
   "publication_remote_id":h["publication_remote_id"],
   "published_commit":commit or self.result,
   "observed_changed_paths":changed or list(h["changed_paths"]),
   "evidence_refs":["git:remote-head","tests:remote-green"],"result_verified":True,
   "authorizes_product_write":False,"authorizes_shared_branch_write":False,
   "authorizes_force_push":False,"authorizes_merge":False,"authorizes_release":False,
   "authorizes_scope_expansion":False,"authorizes_scheduler_mutation":False}

 def verify(self,p,h,**kw):
  return m.validate_publication_proof(
   p,h,self.repo,remote=kw.pop("remote","origin"),
   trusted_repository=kw.pop("trusted_repository",self.repository),
   trusted_remote_id=kw.pop("trusted_remote_id",self.remote_id),**kw)

 def make_patch(self,base,commit,path="result.patch"):
  payload=subprocess.check_output(["git","-C",str(self.repo),"diff","--binary",base,commit])
  target=self.repo/path;target.write_bytes(payload);return target,payload

 def artifact_handoff(self,base=None,commit=None,path="result.patch"):
  base=base or self.base;commit=commit or self.result
  _,payload=self.make_patch(base,commit,path);h=self.direct(commit)
  h.update(transport="content_artifact",source_result_commit=None,direct_result_commit=None,
   artifact_ref={"path":path,"sha256":"sha256:"+hashlib.sha256(payload).hexdigest(),"format":"unified_diff"})
  return h,payload

 def bundle_handoff(self):
  bundle=self.repo/"result.bundle"
  subprocess.check_call(["git","-C",str(self.repo),"bundle","create",str(bundle),"worker-a"],stdout=subprocess.DEVNULL)
  payload=bundle.read_bytes();h=self.direct()
  h.update(transport="content_artifact",direct_result_commit=None,
   artifact_ref={"path":"result.bundle","sha256":"sha256:"+hashlib.sha256(payload).hexdigest(),"format":"git_bundle"})
  return h,bundle,payload

 def test_direct_publication_green_on_bound_remote(self):
  h=self.direct();p=self.proof(h)
  self.assertTrue(self.verify(p,h)["result_verified"])

 def test_local_only_branch_is_not_publication(self):
  subprocess.check_call(["git","-C",str(self.repo),"push","-q","origin",":refs/heads/worker-a"])
  h=self.direct();p=self.proof(h)
  with self.assertRaisesRegex(ValueError,"authoritative remote branch"):
   self.verify(p,h)

 def test_remote_ref_mismatch_is_rejected(self):
  self.push("origin",self.base)
  h=self.direct();p=self.proof(h)
  with self.assertRaisesRegex(ValueError,"exact authoritative remote branch head"):
   self.verify(p,h)

 def test_repointed_origin_is_rejected_by_bound_identity(self):
  h=self.direct();p=self.proof(h)
  self.git("remote","set-url","origin",str(self.alt))
  self.push("origin","worker-a")
  with self.assertRaisesRegex(ValueError,"remote identity mismatch"):
   self.verify(p,h)

 def test_alternate_remote_with_same_commit_is_rejected(self):
  self.push("alt","worker-a")
  h=self.direct();p=self.proof(h)
  with self.assertRaisesRegex(ValueError,"remote identity mismatch"):
   self.verify(p,h,remote="alt")

 def test_split_fetch_push_configuration_is_rejected(self):
  h=self.direct();p=self.proof(h)
  self.git("remote","set-url","--add","--push","origin",str(self.alt))
  with self.assertRaisesRegex(ValueError,"one identical fetch/push endpoint"):
   self.verify(p,h)

 def test_wrong_trusted_repository_is_rejected(self):
  h=self.direct();p=self.proof(h)
  with self.assertRaisesRegex(ValueError,"repository identity mismatch"):
   self.verify(p,h,trusted_repository="example/other")

 def test_wrong_trusted_remote_fingerprint_is_rejected_without_url_leak(self):
  h=self.direct();p=self.proof(h)
  secret_url="https://user:supersecret@example.invalid/private.git"
  self.git("remote","set-url","origin",secret_url)
  try:
   self.verify(p,h)
  except ValueError as exc:
   msg=str(exc)
   self.assertNotIn("supersecret",msg);self.assertNotIn(secret_url,msg)
  else:
   self.fail("repointed credential-bearing remote unexpectedly accepted")

 def test_missing_trusted_identity_is_rejected(self):
  h=self.direct();p=self.proof(h)
  with self.assertRaisesRegex(ValueError,"trusted publication identity"):
   m.validate_publication_proof(p,h,self.repo,remote="origin")

 def test_publication_proof_binds_handoff_digest(self):
  h=self.direct();p=self.proof(h);p["handoff_ref"]="sha256:"+"0"*64
  with self.assertRaisesRegex(ValueError,"handoff_ref mismatch"):self.verify(p,h)

 def test_direct_result_identity_mismatch_fails(self):
  h=self.direct();p=self.proof(h,commit=self.base)
  with self.assertRaisesRegex(ValueError,"direct publication commit mismatch"):self.verify(p,h)

 def test_unified_diff_authenticated_apply_to_base_matches_published_tree(self):
  h,_=self.artifact_handoff();p=self.proof(h)
  self.assertTrue(self.verify(p,h,evidence_root=self.repo)["result_verified"])

 def test_invalid_unified_diff_rejected_before_publication(self):
  bad=self.repo/"result.patch";bad.write_bytes(b"not-a-patch")
  h=self.direct();h.update(transport="content_artifact",source_result_commit=None,direct_result_commit=None,
   artifact_ref={"path":"result.patch","sha256":"sha256:"+hashlib.sha256(bad.read_bytes()).hexdigest(),"format":"unified_diff"})
  with self.assertRaisesRegex(ValueError,"syntactically valid unified_diff"):m.publication_plan(h,self.repo)

 def test_artifact_digest_mismatch_rejected(self):
  (self.repo/"result.patch").write_bytes(b"actual")
  h=self.direct();h.update(transport="content_artifact",source_result_commit=None,direct_result_commit=None,
   artifact_ref={"path":"result.patch","sha256":"sha256:"+"0"*64,"format":"unified_diff"})
  with self.assertRaisesRegex(ValueError,"digest mismatch"):m.publication_plan(h,self.repo)

 def test_unified_diff_manifest_mismatch_rejected(self):
  h,_=self.artifact_handoff();h["changed_paths"]=["src/other.txt"];p=self.proof(h,changed=["src/other.txt"])
  with self.assertRaises(ValueError):self.verify(p,h,evidence_root=self.repo)

 def test_bundle_verification_uses_authenticated_payload_snapshot(self):
  h,bundle,_=self.bundle_handoff();p=self.proof(h);original=m.resolve_artifact
  def swapped(handoff,evidence_root):
   payload=original(handoff,evidence_root);bundle.write_bytes(b"swapped-after-authentication");return payload
  with mock.patch.object(m,"resolve_artifact",side_effect=swapped):
   self.assertTrue(self.verify(p,h,evidence_root=self.repo)["result_verified"])

 def test_bundle_preserves_source_result_identity(self):
  h,_,_=self.bundle_handoff();p=self.proof(h)
  self.assertTrue(self.verify(p,h,evidence_root=self.repo)["result_verified"])
  p["published_commit"]=self.base
  with self.assertRaisesRegex(ValueError,"preserve source result commit"):
   self.verify(p,h,evidence_root=self.repo)

 def test_authority_escalation_rejected(self):
  h=self.direct();p=self.proof(h);p["authorizes_merge"]=True
  with self.assertRaisesRegex(ValueError,"must remain false"):self.verify(p,h)

if __name__=="__main__":unittest.main()
