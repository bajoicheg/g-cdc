CDC sha256:1c06691c0688667d624d1a519c48c0f437ab4951e072f065d9a5e34eec4756be development-a39b0b7ded7e4e11abae424f8b38d875-a1

The functional pilot completed its single permitted layout check successfully. The repository began at the required clean base, the sole scoped document was the only changed path at scope capture, and HEAD remained unchanged; platform gates were not run.

```json
{
  "schema": "codex-cloud-development-report/v1",
  "task_id": null,
  "provider_attempt": 1,
  "operation_key": "sha256:1c06691c0688667d624d1a519c48c0f437ab4951e072f065d9a5e34eec4756be",
  "attempt_id": "development-a39b0b7ded7e4e11abae424f8b38d875-a1",
  "repository": "bajoicheg/g-cdc",
  "environment_id": "6ab67f89058481918ad0bae0282c26f4",
  "base_sha": "725050e4423df4bf612befc91288f9054b5f5a4b",
  "head_before": "725050e4423df4bf612befc91288f9054b5f5a4b",
  "changed_paths": [
    "docs/execution/codex-development-pilot-result-a39b0b7ded7e4e11abae424f8b38d875.md"
  ],
  "checks": [
    {
      "id": "layout",
      "argv": [
        "python",
        "-B",
        "bootstrap/repository_layout.py"
      ],
      "exit_code": 0,
      "test_count": null,
      "log_sha256": "62852d479c54bb10e1f91522251fe019860f88c5a64d4256afe23e7174cc6479"
    }
  ],
  "evidence_refs": [
    "codex-cloud-development-evidence/v1 object in this document"
  ]
}
```

```json
{
  "schema": "codex-cloud-development-evidence/v1",
  "identity_provenance": {
    "repository": {
      "value": "bajoicheg/g-cdc",
      "source": "host-supplied development request",
      "independently_observed": false,
      "conflict_observed": false
    },
    "environment_id": {
      "value": "6ab67f89058481918ad0bae0282c26f4",
      "source": "host-supplied development request",
      "independently_observed": false
    },
    "task_id": {
      "value": null,
      "source": "unavailable"
    },
    "repository_observation": {
      "argv": [
        "git",
        "remote",
        "-v"
      ],
      "exit_code": 0,
      "log_utf8": "",
      "log_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "interpretation": "No configured remote was observed; absence alone is not a repository identity conflict."
    }
  },
  "base_sha": "725050e4423df4bf612befc91288f9054b5f5a4b",
  "head_before": "725050e4423df4bf612befc91288f9054b5f5a4b",
  "head_after": "725050e4423df4bf612befc91288f9054b5f5a4b",
  "clean_before": true,
  "platform_gates": "NOT_RUN",
  "git_checks": {
    "head_before": {
      "argv": ["git", "rev-parse", "HEAD"],
      "exit_code": 0,
      "log_utf8": "725050e4423df4bf612befc91288f9054b5f5a4b\n",
      "log_sha256": "8afea0caf0d6d000369301c36aa2bf44b8fd28deaf6813a343ee937b0ee98f1c"
    },
    "clean_before": {
      "argv": ["git", "status", "--porcelain", "--untracked-files=all"],
      "exit_code": 0,
      "log_utf8": "",
      "log_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "head_after": {
      "argv": ["git", "rev-parse", "HEAD"],
      "exit_code": 0,
      "log_utf8": "725050e4423df4bf612befc91288f9054b5f5a4b\n",
      "log_sha256": "8afea0caf0d6d000369301c36aa2bf44b8fd28deaf6813a343ee937b0ee98f1c"
    },
    "scope_after": {
      "argv": ["git", "status", "--porcelain", "--untracked-files=all"],
      "exit_code": 0,
      "log_utf8": "?? docs/execution/codex-development-pilot-result-a39b0b7ded7e4e11abae424f8b38d875.md\n",
      "log_sha256": "7d984488bdc51c1aa98cd2fea771074197b697d4f7ad68224e624b316b55fd9a"
    }
  },
  "checks": [
    {
      "id": "layout",
      "argv": ["python", "-B", "bootstrap/repository_layout.py"],
      "exit_code": 0,
      "test_count": null,
      "log_utf8": "LAYOUT_GREEN: 513 tracked paths inspected\n",
      "log_sha256": "62852d479c54bb10e1f91522251fe019860f88c5a64d4256afe23e7174cc6479"
    }
  ]
}
```
