# FAST / MEDIUM / FULL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Предлагаемый метод — Native: один исполнитель в текущей сессии; независимые ревью общего изменения перед выпуском согласно действующим требованиям CDC.

**Goal:** Сократить повторные проверки через уровни качества и достоверное повторное использование доказательств.

**Architecture:** Добавить необязательную политику качества и два версионированных контракта для ревью и повторного использования. Старые адаптеры и v1-контракты сохраняют семантику. Каждый результат валидатора является доказательством, не полномочием.

**Tech Stack:** Python 3, unittest, JSON, YAML, существующие валидаторы CDC.

**Spec:** `CDC-FAST-MEDIUM-FULL-design-2026-10-07.md` — согласована пользователем 7 октября 2026, 11:13 МСК. При переносе в канонический репозиторий оба документа помещаются в `docs/superpowers/specs/2026-10-07-quality-levels-design.md` и `docs/superpowers/plans/2026-10-07-quality-levels.md`.

## Global Constraints

- MEDIUM — рекомендуемый уровень для новых проектов; старые проекты сохраняют прежние требования до явной миграции.
- Эффективный уровень равен более строгому из уровня проекта и уровня риска.
- Ядро CDC, права исполнителя, аутентификация, изменения записей AD и опасные миграции требуют FULL.
- Обязательные платформенные, продуктовые и владельческие условия применяются поверх уровня.
- Не подменять candidate_sha исходного запуска новым SHA.
- Дефолт допускает один первичный цикл и один цикл после исправления; следующий требует пересмотра стратегии и причины.
- Действующие лимиты внешних запусков сохраняются. Недоступный учёт токенов явно отмечается.
- Выпущенный 2.11.9 остаётся неизменным. Работа над portable-сборкой GAdControl в другом чате исключена из этой задачи.
- Номер нового выпуска назначается через канонический roadmap; план не объявляет версию или выпуск состоявшимися.

## Review Focus

1. Отсутствующая настройка у старого потребителя не должна автоматически снижать требования — тест задачи 1.
2. Уровень FAST не должен позволять обход FULL переименованием опасного изменения — тест задачи 1.
3. MEDIUM не должен принимать ревью от самого исполнителя или неполное объединённое ревью — тест задачи 2.
4. Неизменный исходный код при изменившейся среде не делает прежние тесты действительными — тест задачи 3.
5. Исчерпание бюджета не должно превращать обязательный непроведённый тест в успешный — тест задачи 4.

---

### Task 0: Подготовить каноническую область работы

**Files:** канонические `AGENTS.md`, `docs/roadmap.md`, текущий adapter/checkpoint, документы из Spec.

- [ ] Прочитать актуальные канонические инструкции, roadmap, незавершённые ветки и ownership. Не использовать старые scratch-копии как доказательство удалённого состояния.
- [ ] Выбрать незанятую изолированную ветку через using-git-worktrees и действующие CDC-права. При занятом источнике работать с изолированным чтением до допустимой записи.
- [ ] Сохранить согласованные документы в каноническом репозитории и оформить admission следующего выпуска без изменения immutable 2.11.9.

### Task 1: Политика качества и эффективный уровень

**Files:** Create `scripts/quality_levels.py`, `tests/test_quality_levels.py`, `templates/quality-assessment.json`; Modify `scripts/validate_adapter.py`, `templates/development-cycle.yaml`, тесты adapter.

**Interfaces:** `validate_policy(data: dict) -> dict`; `evaluate(data: dict) -> dict`; вход `quality-assessment/v1`, выход `quality-assessment-result/v1`.

Необязательный adapter-блок `quality`: `default_level` (FAST/MEDIUM/FULL), `max_validation_cycles` (положительное целое, дефолт 2). Новый шаблон устанавливает MEDIUM; отсутствие блока обозначает legacy, а не MEDIUM.

Assessment содержит `project_level`, `risk_level`, `risk_categories`, `risk_reason`, `mandatory_check_ids`. Категории риска — `cdc_core`, `executor_authority`, `authentication`, `ad_write`, `dangerous_migration`, `ordinary_feature`, `local_reversible`, `documentation`, `presentation`. Пять первых принудительно FULL; ordinary_feature минимум MEDIUM; остальные минимум FAST. Неизвестная категория отклоняется. При повышении требуется непустая причина. Список обязательных проверок сохраняется без удаления.

- [ ] Добавить RED-тесты: FAST+ordinary_feature → MEDIUM; FAST+ad_write → FULL; FULL+documentation → FULL; неизвестная категория → ValueError; отсутствие quality сохраняет legacy; обязательная Windows-проверка остаётся.
- [ ] Запустить `python3 -B -m unittest discover -s tests -p 'test_quality_levels.py' -v`; убедиться в поведенческом RED.
- [ ] Реализовать интерфейсы и подключить необязательный блок к adapter-валидатору без изменения старых ограничений.
- [ ] Запустить новые тесты и существующие adapter-тесты; требуется GREEN.
- [ ] Зафиксировать изменения с их доказательствами.

### Task 2: Ревью по уровню с сохранением v1

**Files:** Modify `scripts/review_pipeline.py`, `tests/test_review_pipeline.py`; Create `templates/review-pipeline-v2.json`.

**Interfaces:** существующий `evaluate(data: dict) -> dict` принимает v1 без изменения и новый `review-pipeline/v2`. V2 содержит `change_id`, `implementer_ref`, `assessment`, `self_review`, `combined_review`, `spec_compliance`, `code_quality`. Assessment — вход задачи 1; эффективный уровень вычисляется валидатором, не принимается на доверии.

Review-запись использует существующие state/reviewer_ref/sequence/evidence_refs/findings; combined дополнительно имеет `covers: [requirements, quality]`. FAST требует GREEN self_review от implementer_ref. MEDIUM требует GREEN combined с двумя областями и reviewer_ref, отличным от implementer_ref. FULL требует отдельные GREEN spec/quality, упорядоченные и независимые друг от друга и исполнителя. Неиспользованные записи — строго not_run. Открытые findings блокируют GREEN. Результат не даёт полномочий.

- [ ] Добавить RED-тесты трёх уровней; отказ MEDIUM при авторевью и неполном covers; отказ при открытых findings; FULL для ad_write несмотря на FAST проекта.
- [ ] Запустить `python3 -B -m unittest discover -s tests -p 'test_review_pipeline.py' -v`; сохранить поведенческий RED новых сценариев.
- [ ] Реализовать отдельную ветку v2, сохранив v1 и его результат.
- [ ] Выполнить тот же набор; все старые и новые тесты GREEN.
- [ ] Зафиксировать изменения.

### Task 3: Явное повторное использование доказательств

**Files:** Create `scripts/evidence_reuse.py`, `tests/test_evidence_reuse.py`, `templates/evidence-reuse.json`; Modify `scripts/verification_gate.py`, `tests/test_verification_gate.py`; Create `templates/verification-gate-v2.json`.

**Interfaces:** `evidence_reuse.validate(data: dict) -> dict`; `evidence_reuse.evaluate(data: dict) -> dict`. Вход `evidence-reuse/v1` содержит `check_id`, `source_candidate_sha`, `target_candidate_sha`, `source_evidence_ref`, `source_state`, `original_inputs`, `current_inputs`, `coverage_refs`, `exact_candidate_required`.

Inputs: `dependency_fingerprints` (непустой словарь путей/идентификаторов и SHA256), `argv` (непустой список строк), `parameters` (объект), `environment_fingerprint` (SHA256), `check_definition_fingerprint` (SHA256). Равенство — по каноническому JSON, порядок argv значим. GREEN требует исходный success, совпадение всех входов, непустые coverage_refs; exact_candidate_required запрещает перенос между SHA. Все отличия выдаются причинами инвалидирования. Доказательство покрывает только заявленные зависимости; полноту покрытия проверяет независимое ревью, валидатор не читает произвольную файловую систему.

Verification-gate/v2 оставляет все действующие поля v1 и добавляет `reused_checks`; каждый элемент — вход evidence_reuse. Идентификаторы обычных и reused checks уникальны и не пересекаются. target SHA совпадает с expected_head. Неприменимое доказательство блокирует завершение. V1 сохраняет строгую SHA-семантику. Источники HEAD/ownership/checkpoint продолжают требовать свежую проверку.

- [ ] Добавить RED-тесты совпадающих зависимостей при двух SHA; изменение argv, среды, параметров и одной зависимости; exact_candidate_required; failed source; пустое покрытие; дубли check_id; старый v1 с wrong_sha по-прежнему отклоняется.
- [ ] Запустить оба целевых unittest-набора; сохранить RED новых сценариев.
- [ ] Реализовать оба интерфейса и явную ветку verification-gate/v2.
- [ ] Повторить целевые тесты; все GREEN, права результата остаются false.
- [ ] Зафиксировать изменения.

### Task 4: Бюджет циклов и рабочие инструкции

**Files:** Modify `scripts/quality_levels.py`, `tests/test_quality_levels.py`, `SKILL.md`, `references/behavioral-tdd-and-verification.md`; Create `references/quality-levels.md`, `templates/validation-cycle.json`; добавить сценарии в существующий behavioral eval suite по его действующему формату.

**Interfaces:** `evaluate_cycle(data: dict) -> dict`; вход `validation-cycle/v1`: `cycle_number`, `max_validation_cycles`, `changed_inputs`, `risk_reason`, `prior_evidence_insufficient_reason`, `strategy_revision_ref`, `budget_observation`.

Cycle 1 допускается при положительных лимитах. Любой повтор требует непустые changed_inputs, risk_reason и prior_evidence_insufficient_reason. Превышение max_validation_cycles дополнительно требует strategy_revision_ref; без него результат REPLAN_REQUIRED. Результат — рекомендация, не право внешнего запуска. budget_observation фиксирует наблюдаемые time/tokens/starts, недоступные метрики null с причиной; лимиты существующего CDC проверяются отдельно.

- [ ] Добавить RED-тесты повторного неизменного цикла, третьего цикла без пересмотра, третьего с пересмотром; доказать, что REPLAN_REQUIRED не преобразует missing required check в success.
- [ ] Выполнить целевой unittest-набор; записать RED.
- [ ] Реализовать evaluate_cycle и обновить инструкции: отчётная правка не инвалидирует неизменные тестовые входы; усыновление пакета использует точную установку и compatibility, без автоматического полного ретеста пакета.
- [ ] Добавить pressure-сценарии: агент не повторяет тест после отчётной правки; повышает AD до FULL; пересматривает стратегию вместо бессмысленного следующего цикла.
- [ ] Выполнить целевые unit/behavioral проверки; GREEN; зафиксировать изменения.

### Task 5: Проверить и выпустить CDC

**Files:** текущие канонические release/CI/package инструменты, версии и evidence нового выпуска; не менять старые release-refs.

- [ ] Проверить всё изменение по FULL: независимые требования и качество, включая корректность dependency coverage и безопасный источник risk_categories. Исправления проверять по изменённым областям, без автоматического повторения неизменных наборов.
- [ ] Выполнить один полный применимый набор пакета после заморозки кандидата и независимый bootstrap под выпущенным CDC 2.11.9; использовать существующие команды release-policy из актуального репозитория.
- [ ] Выполнить требуемые fault/cleanconsumer/platform/CI-проверки в пределах действующих бюджетов. Сохранить SHA, команды, среду и покрытие; дополнительный запуск обосновать изменением входов или недостаточностью доказательства.
- [ ] Проверить терминальный gate и выпустить неизменный новый пакет по действующим каноническим правилам. Установить личный навык с необходимой git-синхронизацией и проверкой точного пакета.

### Task 6: Мигрировать потребителей и измерить эффект

**Files:** adapter, lock, checkpoint и vendored CDC доступных потребителей; Fleet только в рамках текущих полномочий и безопасной границы.

- [ ] Явно выбрать уровень каждого проекта: обычные приложения MEDIUM, критические проекты FULL; UI/текстовые изменения FAST только если политика проекта это разрешает. Не назначать уровень только по имени репозитория.
- [ ] Проверить точную установку и совместимость каждого нового adoption; повторно использовать проверенный пакет, сохранив обязательные продуктовые/платформенные условия и owner pause.
- [ ] GAdControl передать миграцию действующему владельцу либо дождаться безопасной границы; не писать одновременно с другим чатом.
- [ ] На следующих подходящих функциональных задачах записывать доступные время/токены, циклы проверки и возвраты из-за дефектов. Не повторять завершённый rollout 2.11.9 ради измерений.
- [ ] Завершить с фактическими состояниями выпущено/установлено/мигрировано/ожидает владельца; сокращение расходов заявлять только по наблюдениям.

## Self-review

Спецификация покрыта задачами 1–6. V1, отсутствие нового блока, платформенные ограничения и SHA-эквивалентность рассмотрены явно. Контракты и сигнатуры согласованы между задачами. Конкретные release-команды устанавливаются из актуального канонического репозитория в задаче 0; scratch-копии не задают полномочий. Реализация ещё не начата; план ожидает согласования и выбора метода исполнения.
