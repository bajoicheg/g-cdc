# CDC 2.11.7: Codex development — Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans for native execution, or superpowers:subagent-driven-development if explicitly selected. Steps use checkbox syntax.

Goal: перенести разработку и переносимые проверки в Codex; оставить GitHub источником кода и необходимых платформенных проверок.

Architecture: облачная управляющая задача сохраняет существующие lease, managed runtime и единственного интегратора проекта. Новый Cloud Development возвращает проверяемый patch через существующий managed-executor-handoff/v1. Старый COMPUTE_ONLY остаётся отдельным контрактом.

Tech Stack: Python standard library, unittest, Git, официальная Codex CLI, существующие CDC managed runtime/coordination/budget, GitHub Actions для обязательных gates.

Spec: утверждённый 06.10.2026 CDC_compute_design_2026-10-06.txt, рядом с этим файлом. При начале исполнения сохранить его содержимое в docs/superpowers/specs/2026-10-06-codex-development-design.md, этот план — в docs/superpowers/plans/2026-10-06-codex-development.md канонического bajoicheg/g-cdc. Сейчас документы представлены для review; commits ещё не созданы.

## Global Constraints

- Разработка и переносимые проверки выполняются в Codex; GitHub хранит код и выполняет необходимые платформенные проверки.
- COMPUTE_ONLY сохраняется для проверки замороженного кандидата.
- В первом этапе применяется один облачный разработчик на проект.
- Потерянный ответ на запуск означает поиск уже созданной задачи, а не повторный запуск.
- READY провайдера не означает PASS. Невыполненные проверки остаются NOT_RUN.
- UNKNOWN не освобождает резерв. Произвольное извлечение внутренних API и копирование credential-файлов не допускаются.
- Планируемый кандидат — 2.11.7; выполнять под выпущенным 2.11.6, bootstrap floor 2.11.3 сохранить. Это предложение версии, не утверждение о выпуске.
- Зафиксировать main перед работой; наблюдавшийся main 9f0bb607f2158503d1a49ccfee3ffba0228e30b4, release/v2.11.6 b3b517fb70e2deea4006e265f708f29881377885. Изменившуюся базу перечитать, не перезаписывать.
- Существующие schedulers остаются paused. Не менять billing, публичность, permissions и продуктовые версии. Не сбрасывать прежние worktrees/Codespaces с незакоммиченными изменениями.
- Бюджет первой волны: один capability probe, одна активная cloud-задача на проект, максимум две попытки логической задачи; вторая только после конкретного исправления. 45 минут — порог остановки новых запусков и эскалации наблюдения, а не обещание принудительной отмены. Автоматический платный fallback запрещён. Фактические credits брать из dashboard; неизвестный остаток не подменять оценкой.

## Review Focus

1. Среда относится к другому репозиторию или worker не начинает с base_sha: reject до публикации; тест Task 2.
2. Ответ exec потерян и процесс перезапущен: ровно один dispatch, UNKNOWN сохраняет резерв; тест Task 2.
3. Patch выходит за assigned paths, содержит traversal/несовпадающий hash: reject существующим handoff validator; тест Task 3.
4. HEAD изменился либо интегратор утратил lease: никакой публикации; тест Task 3.
5. Исчерпан бюджет, cancel не поддерживается, provider READY без отчёта: запрет нового запуска, сохраняемый guard, без PASS; тест Tasks 1–3.

## File map

В g-cdc P означает src/continuous-development-cycle (все пути ниже с P раскрывать буквально). Новые scripts/codex_cloud_development.py и templates/codex-cloud-development-request.json отвечают только за отдельный developer contract и transport; tests/test_codex_cloud_development.py — за его состояния. scripts/codex_development_bridge.py и tests/test_codex_development_bridge.py связывают его с существующими handoff/budget/ownership механизмами. Существующие scripts/codex_cloud_cli.py, managed_executor_handoff.py, managed_executor_runtime.py и cost_router.py используются как границы и регрессионные проверки; изменение их семантики не требуется. P/references/codex-compute.md описывает два режима; P/scripts/validate_package.py регистрирует новый template. Документы исполнения находятся вне immutable package, в docs/execution/.

### Task 1: доказать облачный управляющий маршрут

Files: docs/execution/codex-controller-capabilities-2026-10-06.json; документы Spec/Plan по указанным выше путям. Это operational qualification, не разработка нового probe framework.

Interfaces: capability receipt содержит schema=cdc-codex-controller-capabilities/v1, observed_at, repository, environment_id, cli_version, base_sha, checks (git_native, coordination_cas, submit, observe, diff_export, validation_report, provider_quiescence), evidence_refs и verdict=qualified|blocked. Каждая проверка имеет passed|failed|not_run и ссылку на доказательство; qualified допустим только при passed всех проверок.

- [ ] Зафиксировать актуальную базу и получить действующее владение g-cdc через существующую координацию в bajoicheg/codex-compute; архивную release-конфигурацию не принимать за текущий lease. Сохранить утверждённые документы под этим владением.
- [ ] В самой среде Codex проверить `codex --version`, `codex cloud --help`, `git ls-remote` канонического repo и обычный Git publish/CAS на отдельном coordination ref с readback. Work-коннектор сам по себе не доказывает native Git auth. Секреты и auth files не переносить.
- [ ] Под существующим one-use launch gate выполнить один ограниченный probe: isolated branch с зафиксированной базой, один изменяемый docs-файл, никаких source push от worker. Использовать официальные `codex cloud exec --env <verified-env> --branch <probe-branch> --attempts 1 <prompt>`, `list --json` с полной пагинацией, `status <task>` и `diff <task> --attempt 1`. Зафиксировать ID, base, patch digest и проверочный отчёт с exit codes/log hashes.
- [ ] Доказать завершение внешней задачи и способность восстановить наблюдение после прерывания контроллера. В CLI 0.160.0 команды cancel нет: подтвердить поддержанный способ provider quiescence; если он отсутствует, завершить probe естественно, отметить ограничение, не заявлять hard runtime cap. Отрицательная проверка: без quiescence guard не освобождается.
- [ ] Записать receipt. При failed/not_run остановить миграцию с конкретным capability blocker; не называть перенос завершённым и не ослаблять модель владения. Временный Codespace допустим только как отдельно учитываемый fallback; зависимость от него не проходит приёмку пилота.
- [ ] При qualified сохранить документы и receipt одним process-only commit; проверить фактический commit readback и освобождение временного probe-владения. Переходить к Task 2 только с qualified.

### Task 2: отдельный Cloud Development transport

Files: create P/scripts/codex_cloud_development.py, P/templates/codex-cloud-development-request.json, P/tests/test_codex_cloud_development.py; modify P/scripts/validate_package.py (template registration), P/references/codex-compute.md.

Interfaces:
- validate_development_request(request: dict) -> dict; ContractError при нарушении.
- CodexCloudDevelopment(journal_root, executable='codex', runner=None, max_pages=1000); submit(request, *, launch_authorized) -> dict; observe(operation_key: str) -> dict; export_diff(operation_key: str, *, evidence_root: Path) -> dict.
- Request exact fields: schema=codex-cloud-development-request/v1, operation_key, attempt_id, repository, environment_id, environment_label, source_branch, base_sha, allowed_paths, acceptance_criteria, checks, budget_ref. SHA/IDs/path rules брать из текущих CDC validators, checks — формат существующего compute request. Один provider attempt на dispatch. Запрещены unknown fields и пустой scope.
- Состояния transport: prepared, submitting, unknown, running, waiting_result, result_exported, failed. ready -> waiting_result. export_diff возвращает task_id, provider_attempt=1, base_sha, artifact_ref={path,sha256,format:unified_diff}; это bytes export, не успешная проверка и не публикация.

- [ ] Создать unittest-тесты: test_wrong_environment_rejected, test_worker_base_mismatch_rejected, test_unknown_request_field_rejected; вход не позволяет сформировать publication authority. Добавить test_submit_once_after_lost_response: число exec=1 после повторного submit и новой инстанции, состояние unknown до reconciliation.
- [ ] Run `python -B -m unittest discover -s P/tests -p test_codex_cloud_development.py -v`; ожидать FAIL из-за отсутствующего нового модуля.
- [ ] Реализовать контракт и transport. Сохранить intent и dispatch_started ДО exec; authorization callback непосредственно перед side effect. Reconcile все страницы inventory по operation/attempt/env; неоднозначность оставляет unknown. Использовать официальную CLI, не `cloud apply`. Вывод diff хранить атомарно под evidence_root, hash вычислить по bytes. Base из request не считать доказательством worker base: подтверждать отдельным отчётом Task 3.
- [ ] Добавить test_ready_without_report_is_waiting_result и test_diff_export_is_read_only; assert ни apply, ни push не вызваны, digest равен bytes, неправильный task/attempt не экспортируется как доверенный результат.
- [ ] Run новую suite и существующую `test_codex_cloud_cli.py`; обе PASS, старый COMPUTE_ONLY не получил прав на изменение. Run package validator после регистрации template; PASS.
- [ ] Commit `feat: add isolated Codex development transport` вместе с документированным контрактом и тестами.

### Task 3: управляемая интеграция и budget admission

Files: create P/scripts/codex_development_bridge.py, P/tests/test_codex_development_bridge.py; modify P/references/codex-compute.md. Существующие managed_* и budget интерфейсы использовать, не создавать второй интегратор.

Interfaces:
- admit_development(request: dict, *, capability_receipt: dict, admission: dict) -> dict: вернуть validated request только при qualified capabilities, действующем lease, принятой reservation и свободном writer slot. admission содержит проверенные existing-runtime evidence_refs, не самовыданный boolean worker.
- build_development_handoff(request: dict, exported: dict, report: dict, *, context: dict, evidence_root: Path) -> dict. context содержит все существующие managed-executor-handoff/v1 identity/publication fields; report exact schema=codex-cloud-development-report/v1, task_id, provider_attempt, operation_key, attempt_id, repository, environment_id, base_sha, head_before, changed_paths, checks (id,argv,exit_code,test_count,log_sha256), evidence_refs. head_before должен равняться base_sha; все identities совпадают. Возвращает существующий content_artifact handoff, без новых publish permissions.
- Передача результата идёт через validate_handoff, resolve_artifact, publication_plan и validate_publication_proof существующего managed_executor_handoff. Контроллер использует прежний managed runtime, а native cloud shell — прежний LocalCommandBackend. Прямой worker push не является transport.

- [ ] Написать test_budget_denial_prevents_dispatch и test_unknown_retains_reservation: при отрицательном existing budget.decide нет exec; при unknown нет release/refund/нового dispatch. test_ready_missing_log_is_not_pass: неполный отчёт не даёт валидный handoff. Тест cancel unsupported сохраняет внешний guard до независимого quiescence evidence.
- [ ] Run `python -B -m unittest discover -s P/tests -p test_codex_development_bridge.py -v`; FAIL из-за отсутствующего bridge.
- [ ] Реализовать два интерфейса поверх существующих validators и ledger; резерв расхода не заменять dashboard balance. Отчёт привязать к bytes patch и scope. Повторные observations не меняют dispatch count и authority. Результат проверяет интегратор в изолированном дереве.
- [ ] Добавить test_patch_scope_escape_rejected, test_artifact_hash_mismatch_rejected, test_head_drift_prevents_publication, test_lease_loss_prevents_publication с существующими handoff/publication fixtures. Assert publication denied для каждой отрицательной ситуации. Добавить test_platform_gate_stays_not_run: Cloud unit PASS не меняет статус Windows/Android runtime gate.
- [ ] Run новые tests плюс existing suites test_managed_executor_handoff.py, test_managed_executor_runtime.py, test_budget.py, test_cost_router.py; все PASS. Полная новая candidate suite не должна регрессировать прежние tests.
- [ ] Commit `feat: integrate Codex development with managed admission and handoff`.

### Task 4: пилот, независимый release и последовательное adoption

Files: create docs/execution/codex-development-pilot-2026-10-06.json и docs/execution/codex-development-adoption-2026-10-06.json; modify P/manifest.json, P/SKILL.md, P/README.md и версионные метаданные ровно по установленному release process. Consumer core materialize из immutable release, вручную не редактировать.

Interfaces: pilot receipt связывает base, provider task, attempts, ledger/evidence refs, patch hash, published commit, checkpoint, final lease/guard readback и actual usage evidence (unknown обозначается явно). Adoption record: по каждому зарегистрированному проекту environment/access, release identity, portable/platform gates, опубликованный SHA и final ownership state. Ни один NEEDS_PLATFORM/NOT_RUN не преобразуется в PASS.

- [ ] Запустить полный g-cdc pilot с одной ограниченной process-задачей через новый contract. Управляющий процесс, Git publish и восстановление выполняются в Codex; постоянный Codespace не нужен. Прервать наблюдение и восстановить без нового dispatch; проверить HEAD drift и budget exhaustion на безопасных fixtures, не через лишние оплачиваемые задачи.
- [ ] Подтвердить published SHA, checkpoint, external quiescence и released lease/guard независимым readback. Сопоставить provider usage с прежним маршрутом, явно отделяя реальные данные от неизвестных. Если usage недоступен, функциональный pilot может быть доказан, экономия — нет; массовое adoption задержать до budget evidence.
- [ ] Проверить кандидат независимо: `python -B bootstrap/repository_layout.py`; из P выполнить `python -B scripts/validate_package.py` и `python -B -m unittest discover -s tests -v`. Ожидать PASS bootstrap/package/full suite; количество тестов записать из реального вывода, не копировать 1027 от старого release.
- [ ] Выполнить отдельные compatibility, fault-injection и минимум три distinct-consumer проверки по canonical release policy; записать evidence каждого класса. Завершить обязательные ordered independent reviews и required release CI. Cloud результаты не заменяют required platform/release checks.
- [ ] Только после gates создать immutable release/v2.11.7 и release identity (commit/package tree/evidence), обновить installed policy. Повторно проверить release identity и version convergence. Commit `release: CDC 2.11.7 Codex development route` без обхода release CI.
- [ ] Прочитать текущий fleet registry и распространять релиз на все зарегистрированные проекты по одному. Для каждого проверить environment/access, границы portable/platform, свободное ownership, exact package tree и lock; process-only adoption не объявлять новой версией продукта. При активном owner/guard отложить конкретный проект, сохранив его работу. Не трогать unrelated projects/Codespaces.
- [ ] Зафиксировать adoption readbacks. Остановить только использованные временные Codespaces после подтверждённого освобождения; подтвердить stopped. Done означает завершённый пилот и adoption каждого доступного проекта либо точный blocker для оставшихся; не включать schedulers автоматически.

## Self-review and execution handoff

Spec coverage: схема 1–3 -> Tasks 1–3; результат/публикация -> Tasks 2–3; platform/расход -> Tasks 1,3,4; пилот/rollout/приёмка -> Task 4. Switcher 2.11.6 уже обновлён, его старый этап не повторять. Пять Review Focus имеют конкретные negative tests. Exported diff не считается доказательством выполнения tests; потребление credits не вычисляется из количества unit tests. Неподдерживаемый native controller — явный ранний blocker, а не скрытая зависимость от Codespaces.

Рекомендованный способ: Native — четыре связанных этапа выполняет текущий исполнитель, затем обязательный независимый branch/release review. Это уменьшает расходы на повторные контексты. Альтернатива Subagent-driven — отдельный implementer/reviewer каждого этапа; дороже, больше промежуточных независимых проверок. Исполнение начинается после review этого плана и выбора способа согласно writing-plans.
