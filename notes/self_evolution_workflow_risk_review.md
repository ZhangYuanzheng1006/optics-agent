# Self-Evolution Workflow Risk Review

> 2026-06-19
> Scope: review of downloaded self-evolution papers under `papers/self-evolution/`, focused on risks in the current `optics_agent` workflow plan.

## Executive Summary

The current `optics_agent` workflow design is a useful orchestration plan, but it is not yet a rigorous self-evolving system. It has a workflow graph, worker/supervisor separation, retry logic, notes, and an `update_artifacts` node. The papers suggest this is insufficient: successful self-evolving systems depend on executable verification, evidence-driven skill lifecycle management, bounded memory/skill injection, replay tests, and rollback gates.

The most important risk is not that the workflow will fail once. The risk is that it will appear to improve while silently accumulating misleading skills, over-generalized lessons, and increasingly brittle workflow edits. This is exactly the pattern described by Library Drift, Skill Shadowing, Forgetting, and Misevolution papers.

Immediate conclusion:

```text
Current plan = workflow orchestration + retrospective editing
Needed plan  = workflow orchestration + verifiers + evidence log + librarian + replay gate
```

## Papers Read

### Failure And Collapse Papers

- `2605.19576` Library Drift: Diagnosing and Fixing a Silent Failure Mode in Self-Evolving LLM Skill Libraries
- `2605.24050` More Skills, Worse Agents? Skill Shadowing Degrades Performance When Expanding Skill Libraries
- `2509.26354` Your Agent May Misevolve: Emergent Risks in Self-evolving LLM Agents
- `2605.09315` Do Self-Evolving Agents Forget? Capability Degradation and Preservation in Lifelong LLM Agent Adaptation
- `2601.22436` Large Language Model Agents Are Not Always Faithful Self-Evolvers
- `2604.16968` On Safety Risks in Experience-Driven Self-Evolving Agents
- `2606.06114` Towards Healthy Evolution: Exploring the Role and Mechanisms of Human-Agent Interaction in Self-Evolving Systems

### Positive Framework Papers

- `2606.07412` Socratic-SWE: Self-Evolving Coding Agents via Trace-Derived Agent Skills
- `2605.22148` Ratchet: A Minimal Hygiene Recipe for Self-Evolving LLM Agents
- `2305.16291` Voyager: An Open-Ended Embodied Agent with Large Language Models
- `2303.11366` Reflexion: Language Agents with Verbal Reinforcement Learning
- `2303.17651` Self-Refine: Iterative Refinement with Self-Feedback

### Survey, Benchmark, And Acceptance Papers

- `2508.07407` A Comprehensive Survey of Self-Evolving AI Agents
- `2606.17546` SEAGym: An Evaluation Environment for Self-Evolving LLM Agents
- `2606.08106` PACE: Anytime-Valid Acceptance Tests for Self-Evolving Agents

## What The Literature Says

### 1. Self-Evolution Needs External Verification

Socratic-SWE works because coding tasks have executable tests and repository-level regression checks. Voyager works because Minecraft exposes environment state, execution errors, inventory changes, and self-verification. Reflexion and Self-Refine work best when the evaluator is reliable and task-specific.

For `optics_agent`, the current `theory_check` and `numerical_check` nodes are still too text-based. A supervisor reading files and deciding pass/fail is useful triage, but it cannot be the final verifier for physics.

Implication:

```text
LLM supervisor < deterministic physical verifier < held-out benchmark
```

Required verifier examples:

- Mie energy conservation: `C_ext = C_sca + C_abs` within tolerance.
- Rayleigh limit: scattering slope near `x^4`.
- Large sphere extinction: `Q_ext -> 2` trend.
- LSPR quasi-static condition: `Re(eps_m) ~= -2 eps_d` for small metal spheres.
- COMSOL result table nonempty and physically ranged.
- Mesh or truncation convergence.
- Paper curve error: RMSE, peak shift, relative error.
- Report verifier: must distinguish `pipeline completed`, `COMSOL job completed`, and `physical reproduction completed`.

### 2. Skill Libraries Fail Without A Librarian

Library Drift and Ratchet show that the problem is not merely whether the LLM can write skills. The problem is lifecycle management. Skills accumulate, retrieval quality falls, stale or wrong skills get injected, and harsh deletion can also destroy useful knowledge.

Current risk in `paper_reproduction.workflow.yaml`:

```yaml
update_artifacts:
  instruction:
    - 将 lessons learned 追加到 SKILL.md 的 Lessons 部分
    - 更新 paper_reproduction.workflow.yaml 本身
```

This directly creates Library Drift risk. A single failed Degiron COMSOL run or a single successful Mie case can become a long-term rule without evidence that it generalizes.

Needed skill lifecycle:

```yaml
skill_item:
  id: string
  status: candidate | active | deprecated
  scope: case | project | global
  domain: mie | comsol | magnus | paper_reading | reporting | safety | workflow
  applies_when: string
  does_not_apply_when: string
  source_capsules: [run_id]
  evidence_count: integer
  positive_cases: [case_id]
  negative_cases: [case_id]
  trial_count: integer
  contribution_score: number
  last_verified: date
  risk_tags: [string]
```

Immediate rule:

```text
Single observation -> candidate note
Repeated evidence -> active skill
Regression evidence -> deprecated, not deleted
```

### 3. More Skills Can Make The Agent Worse

Skill Shadowing reports that expanding a skill library can reduce pass rate because wrong skills shadow the right skill or cause the agent to choose no skill. This is highly relevant here because `optics_agent` has overlapping skills:

- `optics-comsol-runtime`
- `optics-comsol-batch`
- `comsol-java-api`
- `optics-magnus-platform`
- `optics-paper-reproduction`
- Mie analytical work under the paper reproduction skill

Current risk:

```text
Mie Python-only task accidentally loads COMSOL/Magnus lessons.
Degiron-specific COMSOL failures shadow unrelated analytical sphere-array tasks.
COMSOL runtime/image knowledge gets mixed with COMSOL Java API syntax knowledge.
```

Needed change:

- Router must support `NONE`.
- Each node must declare allowed skills.
- Skill injection should be task-type gated, not only semantic similarity based.
- Invocation log must record which skills were loaded and why.

Proposed node metadata:

```yaml
loads_skills:
  allowed:
    - optics-paper-reproduction
    - comsol-java-api
  forbidden:
    - optics-docker-images
  allow_none: true
```

### 4. Self-Evolving Agents Can Forget Old Capabilities

The forgetting paper shows that improving on a new distribution can degrade old tasks. This matters because `optics_agent` has multiple task families:

- paper reading and parameter extraction
- Mie analytical/semi-analytical modeling
- COMSOL Java model generation
- Magnus job submission
- PI-facing reporting
- workflow and skill self-maintenance

Current risk:

```text
Optimizing for Mie analytical tasks may make COMSOL workflow rules stale or hidden.
Optimizing COMSOL failure recovery may overcomplicate simple analytical tasks.
New paper reproduction experience may erase or override earlier reporting boundaries.
```

Needed replay suite:

- one simple Mie analytical case
- one metal sphere LSPR case
- one known COMSOL smoke case
- one known blocked COMSOL case, such as Degiron v2 mode-analysis failure
- one paper-reading-only task
- one report-generation task that must preserve `pipeline/job/physical` distinction

Acceptance condition:

```text
No canonical workflow/skill update is accepted unless replay does not regress.
```

### 5. Condensed Experience Is Often Not Used Faithfully

The Not Faithful paper shows that agents may depend on raw experience but ignore, misunderstand, or superficially use condensed summaries. This means a neat `Lessons` paragraph in `SKILL.md` may not actually guide behavior correctly.

Current risk:

```text
"Degiron v2 mode analysis failed" could be misread as "all SU-8 waveguide mode analysis is impossible".
"Use GUI-exported Java templates" could be over-applied to Python-only Mie theory tasks.
"Do not overclaim reproduction" could remain a slogan but fail to affect final report wording.
```

Needed experience format:

- link to raw trace or run folder
- specific applicability conditions
- explicit non-applicability conditions
- concrete verification checklist
- counterexamples

### 6. Success-Oriented Experience Can Increase Unsafe Execution Bias

Safety-risk papers show that benign successful execution traces can make agents more action-biased: they become more likely to act, submit, modify, or reuse tools when they should stop.

Current project-specific risks:

- submitting Magnus jobs when cluster resource or license state is uncertain
- modifying long-term skills after one failed run
- treating surrogate or diagnostic results as physical reproduction
- continuing blind COMSOL eigenvalue-shift retries after matrix factorization failure
- leaking private paths, license details, or raw private data into public reports
- changing the active COMSOL runtime image or blueprint without explicit request

Needed stop conditions:

```yaml
stop_conditions:
  - missing_required_paper_parameters
  - solver_reaches_eigensolver_but_exports_no_physical_rows
  - result_is_surrogate_or_diagnostic_only
  - same_error_type_repeated_without_new_evidence
  - next_step_requires_human_domain_artifact
```

### 7. Human/Supervisor Feedback Helps Most At Execution-Result Gates

Healthy Evolution suggests supervision is most valuable at execution/result stages, not uniformly at every token. For this project, the high-value gates are:

- before `magnus_submit`
- after `numerical_check`
- before final report language is accepted
- before `update_artifacts` changes canonical files
- before promoting a script to a reusable tool
- before editing AGENTS, skills, workflows, or blueprints

Supervisor should not be treated as a helper that makes completion faster. Its role should be adversarial quality control:

- detect overclaiming
- detect wrong skill injection
- detect unsafe action bias
- detect over-generalized memory
- detect workflow bloat
- detect missing physical verifier evidence

## Main Deficiencies In The Current Plan

### Deficiency 1: `update_artifacts` Writes Canonical Artifacts Too Easily

Current design asks the agent to update skills, blueprints, and workflow files directly after a case. This is the highest-risk part of the plan.

Why it is risky:

- single-case lessons become global instructions
- failed workarounds can be preserved as authoritative rules
- workflow topology can overfit one paper
- skill library can drift or shadow useful skills
- no acceptance test or replay gate is defined

Recommended replacement:

```text
update_artifacts -> propose_artifact_patch -> critic_verdict -> replay_gate -> accept_or_quarantine
```

Default policy:

```text
proposal_only by default
human_gate for high-risk artifacts
auto_write only for low-risk run-local notes
```

### Deficiency 2: Workflow Schema Lacks Risk And Evidence Fields

Current `workflow_schema.yaml` contains only type, instruction, produces, next, branches, and retries. It does not encode risk level, stop conditions, skill loading, memory loading, verifier outputs, replay checks, or artifact-write policy.

Needed schema additions:

```yaml
risk_level: low | medium | high
loads_skills:
  allowed: []
  forbidden: []
  allow_none: true
loads_memories:
  scope: case | project | global
  max_items: integer
success_metrics:
  pipeline: string
  numerical: string
  physical: string
verifiers:
  - name: string
    command: string
    required: true
stop_conditions: []
human_review_conditions: []
regression_checks: []
artifact_write_policy: proposal_only | auto_write | human_gate
```

### Deficiency 3: Supervisor Judgment Is Overloaded

The plan asks the supervisor to judge theory quality, numerical quality, iteration quality, and branch routing. Literature suggests LLM feedback helps, but only when bounded by external signals.

Recommended rule:

```text
Supervisor can explain and route, but cannot be sole evidence for success.
```

For each branch, there should be at least one of:

- deterministic script output
- physical invariant check
- reproducible test command
- frozen benchmark score
- explicit human review

### Deficiency 4: No Attempt Capsule Or Evidence Log

Current notes and logs are human-readable but not enough for self-evolution. Ratchet-style governance requires structured records.

Add:

```yaml
attempt_capsule:
  run_id: string
  case_id: string
  node_id: string
  task_type: string
  selected_skills: []
  selected_memories: []
  commands_run: []
  artifacts_read: []
  artifacts_written: []
  verifier_results: []
  outcome: pass | fail | blocked | surrogate | diagnostic
  failure_type: string
  human_intervention: boolean
```

Add verdict records:

```yaml
critic_verdict:
  capsule_id: string
  attribution: helped | hurt | neutral | inapplicable
  failure_pattern: string
  evidence: string
  confidence: low | medium | high
```

### Deficiency 5: No Held-Out Benchmark Or Replay Split

Without frozen splits, every workflow iteration risks p-hacking the same few cases.

Recommended split:

```text
Dtrain       produces traces and candidate skills
Dupdate-val  accepts or rejects candidate changes
DID-test     same-distribution final test
DOOD-test    different tool/physics/model final test
Dreplay      old capabilities that must not regress
Daudit       final untouched set
```

Early project version can use very small sets, but the split must exist conceptually from the start.

### Deficiency 6: Mie Timeline Is Too Optimistic If It Also Serves As Benchmark Infrastructure

The current Mie plan is useful, but if Mie is also the low-cost benchmark for workflow self-evolution, the first milestone should not be “three papers in one week”. It should be a reliable verifier suite.

Better first milestone:

```text
single-sphere Mie implementation + energy conservation + Rayleigh + large-size extinction + reproducible benchmark manifest
```

Only after this should metal LSPR, core-shell, and arrays become workflow test cases.

## Recommended Design Changes

### Priority 0: Change The Meaning Of `update_artifacts`

Do not let `update_artifacts` directly update canonical skills, workflow, AGENTS, or blueprints.

New behavior:

1. collect attempt capsules
2. cluster failure patterns
3. synthesize candidate skill or workflow patch
4. attach evidence level
5. run schema validation
6. run replay checks
7. supervisor reviews risk
8. accept, quarantine, or reject

Evidence levels:

```text
single_observation -> run-local note only
repeated_evidence -> candidate skill
benchmark_backed -> active skill/workflow patch
human_confirmed -> allowed for high-risk project policy
```

### Priority 1: Add A Minimal Librarian

Implement before large-scale self-iteration.

Minimum features:

- candidate/active/deprecated states
- active cap per domain
- source capsule links
- contribution score or simpler pass/fail counts
- no hard delete
- router can choose no skill
- skill invocation log

Simple first version:

```text
Only promote a lesson to ACTIVE after it helps in at least 2 cases or is human-confirmed.
Deprecate if it appears in 2 failures where it was judged hurtful or inapplicable.
```

### Priority 2: Add Deterministic Verifiers

Start with Mie because it is cheap and gives many examples.

Initial verifier list:

- energy conservation
- Rayleigh slope
- large-size extinction trend
- truncation convergence
- LSPR approximate peak condition
- benchmark curve RMSE

COMSOL verifier list:

- job status
- expected output files exist
- result table nonempty
- physical ranges valid
- mesh convergence if feasible
- not surrogate/fallback unless explicitly labeled

### Priority 3: Add Replay Gate

Each canonical update must run a small replay suite.

Initial replay cases:

- one simple Mie case
- one known Mie edge case
- one COMSOL smoke or known blocked case
- one report-generation boundary case
- one workflow schema validation case

Accept if:

```text
candidate gain on update-val > 0
AND replay regression count = 0 for critical checks
AND cost increase is below threshold
AND no safety/privacy rule is weakened
```

### Priority 4: Add Paired Acceptance Testing

For each candidate patch, compare incumbent vs candidate on the same cases.

Track:

```text
wins: candidate passes, incumbent fails
losses: incumbent passes, candidate fails
ties: both same
forget_count
fix_count
cost_delta
```

For early small-sample work, do not claim statistical significance. Label as smoke evidence or paired diagnostic evidence. For serious claims, use frozen validation and audit sets.

### Priority 5: Separate Short-Term Reflection From Long-Term Skill

Use Reflexion-style short memory only within a case or node retry.

Rules:

- short-term reflection: current case only, max 1-3 items
- case pitfall: stored under case folder, not global skill
- project skill candidate: needs repeated evidence
- global/project policy: needs human confirmation or benchmark evidence

## Concrete YAML Direction

Example updated node skeleton:

```yaml
numerical_check:
  type: branch
  risk_level: high
  loads_skills:
    allowed:
      - optics-paper-reproduction
      - optics-comsol-batch
    allow_none: true
  verifiers:
    - name: result_table_nonempty
      command: python workflows/verifiers/check_result_table.py <case>
      required: true
    - name: physical_range_check
      command: python workflows/verifiers/check_physical_ranges.py <case>
      required: true
  success_metrics:
    pipeline: job_finished_without_runtime_error
    numerical: result_table_nonempty_and_finite
    physical: target_phenomenon_detected_with_threshold
  stop_conditions:
    - same_error_type_repeated_without_new_evidence
    - solver_success_but_no_physical_rows
    - result_is_surrogate_or_diagnostic_only
  human_review_conditions:
    - requires_gui_exported_comsol_template
    - proposes_cluster_resource_increase
  branches:
    pass: answer_verification
    fail: numerical_debug
    blocked: generate_handoff
```

Example `update_artifacts` replacement:

```yaml
propose_artifact_patch:
  type: prompt
  risk_level: high
  artifact_write_policy: proposal_only
  instruction: |
    Create candidate patches only. Do not modify canonical AGENTS, SKILL,
    workflow, blueprint, or reusable tool files.
    Every candidate must cite attempt_capsule ids and declare applicability,
    non-applicability, risk tags, and required replay checks.
  next: artifact_patch_gate

artifact_patch_gate:
  type: branch
  risk_level: high
  verifiers:
    - name: schema_validation
      command: python workflows/verifiers/check_workflow_schema.py
      required: true
    - name: replay_suite
      command: python workflows/verifiers/run_replay.py
      required: true
  branches:
    accept: apply_artifact_patch
    quarantine: end
    reject: end
```

## Experimental Strategy After This Review

### Conservative Claim Ladder

Use these labels to avoid overclaiming:

```text
Level 0: workflow runs a case
Level 1: deterministic verifier passes
Level 2: replay does not regress
Level 3: paired validation shows net gain
Level 4: held-out ID/OOD test confirms improvement
Level 5: statistically supported superiority over baseline frameworks
```

Do not call the workflow “successful self-evolution” before Level 3. Do not claim superiority over other frameworks before Level 4-5.

### Best Near-Term Research Direction

The safest route is not to chase full autonomous self-evolution immediately. The safest route is:

1. Build low-cost Mie verifiers and benchmark manifest.
2. Run baseline workflow without self-modification.
3. Add attempt capsules and structured failure taxonomy.
4. Add proposal-only artifact updates.
5. Add replay gate and librarian.
6. Only then test whether self-evolution improves pass rate.

This still produces useful outputs if the final workflow has no advantage:

- tool/system paper: workflow runner + verifier suite
- empirical paper: failure taxonomy and agent limitations in optical simulation
- negative-result discovery: if drift, shadowing, forgetting, or unsafe execution bias appears in scientific workflows
- dataset/benchmark: Mie + COMSOL reproduction benchmark

## Highest-Risk Current Assumptions

1. A supervisor conversation can reliably judge theory and numerical correctness.
2. Lessons appended to `SKILL.md` will be used faithfully and beneficially.
3. More project memory and skills will monotonically improve performance.
4. A workflow that improves one paper/case will improve future cases.
5. Artifact self-editing can be safe with only syntax validation.
6. COMSOL/Magnus success is close to physical reproduction success.
7. A small number of case studies can support claims about self-evolution effectiveness.
8. Runtime retry budgets are enough to prevent blind debugging loops.

The papers largely argue against all eight assumptions.

## Final Recommendation

Keep the CLI-driven worker/supervisor architecture. Keep YAML workflow definitions. Keep the idea of self-iteration. But demote `update_artifacts` from “automatic self-improvement” to “evidence-gated governance”. Add verifiers, evidence logs, skill lifecycle states, replay tests, and paired acceptance gates before trusting any self-evolved workflow or skill.

Minimal actionable plan:

1. Update workflow schema with `risk_level`, `stop_conditions`, `human_review_conditions`, `verifiers`, `loads_skills`, `success_metrics`, `regression_checks`, and `artifact_write_policy`.
2. Replace direct `update_artifacts` writes with candidate patch generation.
3. Create attempt capsule and critic verdict files for every node execution.
4. Build Mie verifier suite first, before expanding to many papers.
5. Add active/candidate/deprecated lifecycle for lessons and skill items.
6. Add a small replay suite before any canonical workflow or skill update.
7. Report all outcomes with the three-state distinction: pipeline, numerical job, physical reproduction.
