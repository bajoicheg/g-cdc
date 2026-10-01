import copy, json, sys, unittest, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import execution_lease_v2 as v2
import operation_intent as op
from git_lease_store import validate_coordination_record, validate_coordination_transition

OWNER=str(uuid.UUID("11111111-1111-4111-8111-111111111111"))
INV={"invocation_id":"wake-1","automation_id":"auto-1","conversation_id":"chat-1","execution_surface":"managed","started_at_utc":"2026-01-01T10:00:00Z"}

class Store:
    def __init__(self,record):
        self.revision="r0";self.record=copy.deepcopy(record);self.n=0
    def read(self):return self.revision,copy.deepcopy(self.record)
    def compare_and_swap(self,expected,record):
        if expected!=self.revision:raise ValueError("stale")
        self.n+=1;self.revision="r"+str(self.n);self.record=copy.deepcopy(record);return self.revision

class Tests(unittest.TestCase):
    def test_valid_owned_v2_is_supported_by_git_store(self):
        r=v2.acquire(v2.initialize("example/project","refs/heads/main"),OWNER,"2026-01-01T10:00:01Z",invocation=INV)
        self.assertIs(validate_coordination_record(r),r)

    def test_generation58_style_partial_v1_patch_is_rejected(self):
        r=v2.initialize("example/project","refs/heads/main")
        r.update(owner_id=OWNER,generation=1,acquired_at_utc="2026-01-01T10:00:01Z",
                 heartbeat_at_utc="2026-01-01T10:00:01Z",expires_at_utc="2026-01-01T10:20:01Z")
        self.assertIsNone(r["invocation"]); self.assertIsNone(r["finalization"])
        with self.assertRaises((ValueError,TypeError)):
            validate_coordination_record(r)

    def unresolved_claim(self):
        r=v2.acquire(v2.initialize("example/project","refs/heads/main"),OWNER,"2026-01-01T10:00:01Z",invocation=INV)
        intent=json.loads((ROOT/"templates"/"operation-intent.json").read_text())
        intent["created_at_utc"]="2026-01-01T10:00:01Z";intent["updated_at_utc"]="2026-01-01T10:00:01Z"
        intent["binding"]["repository"]="example/project";intent["source_ref"]="refs/heads/main"
        intent["operation_key"]=op.operation_key(intent["binding"])
        receipt=op.verify_readback(intent,copy.deepcopy(intent),"store:intent/1",intent["updated_at_utc"])
        intent=op.transition(intent,"submitting",intent["updated_at_utc"],receipt=receipt)
        r=v2.set_guard(r,OWNER,1,"wake-1","2026-01-01T10:00:02Z",intent,"store:intent/submitting")
        store=Store(r)
        v2.claim_submission(store,"r0","example/project","refs/heads/main",OWNER,1,"wake-1",
                            "2026-01-01T10:00:03Z",intent_digest=r["external_guard"]["intent_digest"])
        return store.read()[1],intent

    def terminal_observation(self,intent,lookup_complete=True):
        task={"task_id":"task-1","task_url":"https://example.invalid/task/1",
              "operation_key":intent["operation_key"],"attempt_id":intent["attempt_id"],
              "binding":copy.deepcopy(intent["binding"]),"state":"terminal",
              "conclusion":"succeeded","evidence_refs":["provider:terminal/1"]}
        return {"schema":"operation-observation/v1","operation_key":intent["operation_key"],
                "observed_at_utc":"2026-01-01T10:00:04Z","lookup_complete":lookup_complete,
                "tasks":[task] if lookup_complete else []}

    def test_exact_clear_guard_resolution_transition_is_accepted(self):
        previous,intent=self.unresolved_claim()
        current=v2.clear_guard(previous,OWNER,1,"wake-1","2026-01-01T10:00:04Z",
                               self.terminal_observation(intent),"provider:terminal/1")
        self.assertIs(validate_coordination_transition(previous,current),current)

    def test_fabricated_resolution_and_guard_clear_without_terminal_observation_is_rejected(self):
        previous,intent=self.unresolved_claim()
        claim=copy.deepcopy(previous["external_guard"]["submission_claim"])
        current=copy.deepcopy(previous)
        observation=self.terminal_observation(intent,lookup_complete=False)
        current["external_guard"]=None
        current["last_terminal"]={
            "operation_key":claim["operation_key"],"intent_digest":claim["intent_digest"],
            "intent_reference":previous["external_guard"]["intent_reference"],
            "observation":observation,"evidence_reference":"provider:fabricated",
            "at_utc":"2026-01-01T10:00:04Z"}
        current["submission_resolutions"].append({
            "grant_id":claim["grant_id"],"owner_id":claim["owner_id"],"generation":claim["generation"],
            "operation_key":claim["operation_key"],"attempt_id":claim["attempt_id"],
            "intent_digest":claim["intent_digest"],"resolved_at_utc":"2026-01-01T10:00:04Z",
            "evidence_reference":"provider:fabricated","observation_digest":op._hash(observation)})
        v2.validate(current)
        with self.assertRaisesRegex(ValueError,"terminal|reconciliation|evidence"):
            validate_coordination_transition(previous,current)

    def test_guarded_submission_cannot_be_raw_cas_cleared_without_resolution(self):
        previous,_=self.unresolved_claim()
        current=copy.deepcopy(previous);current["external_guard"]=None
        with self.assertRaisesRegex(ValueError,"cannot clear"):
            validate_coordination_transition(previous,current)

    def test_v2_cannot_downgrade_to_v1(self):
        previous=v2.initialize("example/project","refs/heads/main")
        legacy=v2.legacy.initialize("example/project","refs/heads/main")
        with self.assertRaisesRegex(ValueError,"cannot downgrade"):
            validate_coordination_transition(previous,legacy)

if __name__=="__main__": unittest.main()
