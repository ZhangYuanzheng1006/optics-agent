# Self-Evolution Workflow Risk Review

> 2026-06-19
> Scope: review of downloaded self-evolution / agent-workflow papers under `papers/self-evolution/`, focused on risks in the current `optics_agent` workflow plan.

## Executive Summary

The current `optics_agent` workflow design is a useful orchestration plan, but it is not yet a rigorous self-evolving system. It has a workflow graph, worker/supervisor separation, retry logic, notes, and an `update_artifacts` node. The expanded 127-paper review suggests this is insufficient: successful self-evolving systems depend on executable verification, evidence-driven skill lifecycle management, bounded memory/skill injection, workflow provenance, benchmark disclosure, sandboxed tool use, replay tests, and rollback gates.

The most important risk is not that the workflow will fail once. The risk is that it will appear to improve while silently accumulating misleading skills, over-generalized lessons, and increasingly brittle workflow edits. This is exactly the pattern described by Library Drift, Skill Shadowing, Forgetting, and Misevolution papers.

Immediate conclusion:

```text
Current plan = workflow orchestration + retrospective editing
Needed plan  = workflow orchestration + verifiers + evidence log + provenance + librarian + replay gate + sandbox
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

### Expanded Workflow, Skill, Memory, Safety, And Scientific-Agent Papers

The review was later expanded to **127 PDFs** with per-folder summaries in `papers/self-evolution/*/README_summaries.md`. The most relevant new groups are:

- `workflow_optimization/`: AFlow, Benchmarking Agentic Workflow Generation, JudgeFlow, QualityFlow, Externalization, workflow provenance.
- `agent_skills/`: Agent Skills, SkillOps, SkillTester, Skill Drift, SkillWiki, SkillRevise, SkillGrad, skill supply-chain and prompt-injection papers.
- `multi_agent_orchestration/`: AgentOrchestra, MAFBench, AutoGen, MetaGPT, CAMEL, Echoing, plan reuse.
- `memory_lifelong/`: Memory for Autonomous LLM Agents, MemEvoBench, memory evaluation, feedback-to-memory, hierarchical procedural memory.
- `evaluation_benchmarks/`: AEMA, LLM agent benchmark audit, uncertainty decomposition, self-evolving agent surveys.
- `safety_governance/`: ToolEmu, AgentDojo, AgentGuard, SafeSearch, VESTA.
- `scientific_agents/`: AI Scientist, AI-Researcher, autonomous scientific discovery surveys, Why LLMs Aren't Scientists Yet.

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

## Additional Risks From The Expanded 127-Paper Review

The first review focused on classic self-evolution failure modes. The expanded literature adds a broader warning: once skills, memories, workflows, tools, provenance stores, and multi-agent roles are externalized, the system can fail even when every single component looks reasonable in isolation.

### 8. Workflow Topology Can Be Wrong Even When The Final Output Looks Good

Papers: `2410.07869` Benchmarking Agentic Workflow Generation, `2410.10762` AFlow, `2601.07477` JudgeFlow.

Current risk:

```text
The generated workflow may omit dependency edges, skip required nodes, or route around weak verifiers while still producing a plausible final report.
```

Examples for `optics_agent`:

- generating code before `physics_formalization` is complete
- comparing plots before unit/material parameters are verified
- running `final_report` from a diagnostic/surrogate output path
- optimizing workflow search against weak rewards such as file existence or report completeness

Controls:

- score workflow structure separately from final result quality
- validate required nodes, dependency edges, and data dependencies
- make workflow reward multi-objective: physical verifier score, topology validity, cost, reproducibility, and report honesty
- require `block_blame` records to include evidence and confidence; low-confidence attribution cannot drive automatic topology edits

### 9. Externalized Harness Components Create Version-Coupling Risk

Papers: `2604.08224` Externalization in LLM Agents, `2509.13978` Workflow Provenance.

Current risk:

```text
AGENTS.md, SKILL.md, workflow YAML, memory search results, tool versions, model versions, and container images jointly determine behavior, but the run may only record the final artifacts.
```

This makes apparent improvements non-attributable. A case may improve because the model changed, a skill changed, memory search returned a different item, a COMSOL image changed, or the workflow changed.

Controls:

```yaml
run_manifest:
  workflow_version:
  case_workflow_hash:
  agents_policy_hash:
  skill_versions: []
  loaded_memories: []
  model:
  inference_params:
  tool_versions: []
  container_or_runtime_digest:
  commands_run: []
  artifacts_read:
    - path:
      hash:
      producer_node:
  artifacts_written:
    - path:
      hash:
      producer_node:
```

Provenance answers must cite artifact IDs and distinguish:

```text
logged fact | inference from logs | missing information | unknown
```

### 10. Skill Artifacts Are Supply-Chain Objects, Not Just Text Instructions

Papers: `2602.12430` Agent Skills, `2604.03081` Supply-Chain Poisoning, `2510.26328` Agent Skills Prompt Injections, `2604.02837` Secure Agent Skills.

Current risk:

```text
A skill can contain SKILL.md prose, code blocks, helper scripts, config files, examples, and resources. Treating only the markdown as the skill misses the actual attack or drift surface.
```

Project-specific risks:

- malicious or wrong backup/sync snippets copied from a skill example
- helper scripts reading `reproduction_test/private/` or secret-adjacent paths despite benign prose
- third-party skill instructions embedded as trusted system-like text
- stale COMSOL/Magnus snippets becoming active operational policy

Controls:

- treat skill packages as supply-chain artifacts: markdown + scripts + configs + resources
- scan for declared vs actual capabilities
- candidate skills are read-only and cannot execute high-risk actions
- promotion requires static review, dry-run behavior, permission declaration, and provenance
- never convert web/PDF/README text directly into active skill instructions

### 11. Skill Behavioral Integrity Can Fail Across Text And Code

Papers: `2605.11770` Behavioral Integrity Verification, `2606.14154` SkillMutator, `2605.00314` Semia.

Current risk:

```text
SKILL.md may say one thing while helper scripts, shell commands, or hidden initialization behavior do something broader.
```

Controls:

```yaml
skill_integrity:
  declared_capabilities: []
  actual_capabilities: []
  privileged_operations: []
  private_path_access: false
  network_access: false
  shell_access: false
  writes_canonical_artifacts: false
  mismatch_policy: block_promotion
```

If actual behavior touches filesystem writes, shell, network, credentials, external services, or canonical artifacts without explicit declaration, the skill must remain quarantined.

### 12. Typed Skill Refactoring Can Lose Applicability Boundaries

Papers: `2605.27955` Skill-as-Pseudocode, `2605.17734` Skill Programs, `2606.01139` SkillRevise, `2605.27760` SkillGrad.

Current risk:

```text
Turning prose lessons into typed contracts, pseudocode, or executable interventions can make them easier to invoke but easier to over-apply.
```

Examples:

- “Degiron v2 mode analysis needed GUI-exported templates” becomes “all COMSOL mode analysis requires template before trying anything”
- “Do not overclaim surrogate results” becomes a generic report blocker that fires on legitimate low-risk diagnostics
- a skill program auto-blocks or rewrites workflow steps beyond its intended scope

Controls:

- every typed/refactored skill must retain source text links
- every action template must define `applies_when` and `does_not_apply_when`
- executable skill programs may diagnose/block but cannot directly execute external actions unless separately approved
- refactoring requires coverage, binding, replacement, and risk checks before promotion

### 13. Multi-Agent Review Can Collapse Into Echoing Or Identity Drift

Papers: `2511.09710` Echoing, `2602.03128` MAFBench, AutoGen/CAMEL/MetaGPT family.

Current risk:

```text
Adding reviewer/expert agents does not guarantee independence. Agents can echo each other, defend previous outputs, or lose role boundaries in long conversations.
```

Project-specific risks:

- reviewer starts summarizing worker claims instead of checking artifacts
- COMSOL expert overrules physics uncertainty because supervisor framed the task as implementation failure
- supervisor compresses context so aggressively that independent reviewer cannot see raw evidence
- multi-agent consensus amplifies a wrong physical interpretation

Controls:

- each role prompt must declare `role`, `object_to_check`, `forbidden_actions`, `required_evidence`, and `confidence`
- reviewer must cite original artifacts/verifier outputs, not only worker text
- role sessions should have bounded turns; long exchanges trigger identity-drift checks
- complex agent group workflows must track coordination cost and allow `single_agent` or `direct_tool` routing for simple tasks

### 14. Plan Reuse And Template Reuse Can Import Wrong Assumptions

Papers: `2512.21309` Plan Reuse Mechanism, workflow-template papers, scientific-agent papers.

Current risk:

```text
case_workflow templates may be selected by semantic similarity but silently carry old geometry, material, solver, or reporting assumptions.
```

Controls:

```yaml
template_contract:
  slots: []
  fixed_assumptions: []
  required_inputs: []
  required_verifiers: []
  does_not_apply_when: []
  forbidden_reuse_conditions: []
```

Template reuse must pass premise matching before execution. Similar title/abstract embedding is not enough.

### 15. Memory Retrieval Can Be Harmful When Memory Types Are Mixed

Papers: `2605.28224` When Does Memory Help, `2507.05257` MemoryAgentBench, `2604.15774` MemEvoBench, `2601.05960` Feedback-to-Memory.

Current risk:

```text
facts, raw observations, failed attempts, reviewer feedback, reflections, procedures, and policy rules are retrieved from the same pool.
```

Consequences:

- failed COMSOL traces can pollute Python-only Mie tasks
- one-off reviewer feedback can become a long-term policy
- old and corrected memories coexist without supersession
- the system remembers an item but does not apply it faithfully in the right node

Controls:

```yaml
loads_memories:
  allowed_types:
    - fact
    - procedure
  forbidden_types:
    - raw_failed_attempt
  scope: project
  max_items: 5
  require_supersession_check: true
```

Memory evaluation should test retrieval, test-time learning, long-range integration, selective forgetting, and conflict resolution.

### 16. Graph Memory Can Freeze Wrong Causal Attributions

Papers: `2602.05665` Graph-based Agent Memory, provenance papers.

Current risk:

```text
Automatically linking failures with `caused_by` or `mitigated_by` edges can turn weak correlations into durable debugging bias.
```

Example:

```text
COMSOL matrix factorization failure -> caused_by eigenvalue shift
```

This may be wrong; the cause may be physics setup, boundary condition, mesh, missing template, or solver configuration.

Controls:

- memory graph edges need `edge_type`, `weight`, `evidence`, and `confidence`
- automatic `caused_by` and `mitigated_by` edges default to low confidence
- verified causes require counterfactual evidence or repeatable verifier checks
- reports must distinguish observed correlation from verified cause

### 17. Benchmark And Evaluation Disclosure Can Be Too Weak To Support Claims

Papers: `2605.21404` benchmark audit, `2601.11903` AEMA, `2507.21504` agent evaluation survey.

Current risk:

```text
The workflow may report pass rate improvements without enough disclosure to reproduce or attribute the improvement.
```

Required disclosure for every benchmark/evaluation run:

- task version and source paper/figure
- harness and workflow versions
- model, parameters, and tool versions
- container/runtime digest
- cost, retries, wall time, and human interventions
- failure taxonomy
- replay regression results
- raw verifier outputs

LLM evaluator pass must never be merged with deterministic verifier pass. Final reports should use separate labels:

```text
LLM evaluator pass
deterministic verifier pass
physical verifier pass
human domain-review pass
```

### 18. Uncertainty Must Be Routed, Not Averaged Into One Confidence Score

Papers: `2606.19559` Uncertainty Decomposition, scientific-agent failure papers.

Current risk:

```text
The agent says it is confident, but the uncertainty is actually about missing user/domain inputs, not action execution.
```

For paper reproduction this is critical: missing material constants, boundary conditions, scan ranges, GUI-exported COMSOL templates, or figure definitions should route to clarification, not debugging.

Controls:

```yaml
uncertainty:
  action_confidence: low | medium | high
  request_uncertainty: low | medium | high
  missing_fields: []
  underspecified_inputs: []
  route_if_high_request_uncertainty: clarification_or_blocked
```

### 19. External Content And Tool Output Are Indirect Prompt-Injection Surfaces

Papers: `2406.13352` AgentDojo, `2509.23694` SafeSearch, tool-use benchmark papers.

Current risk:

```text
PDF text, webpages, logs, README files, code comments, search results, and tool outputs may contain instructions that the agent treats as operational guidance.
```

Controls:

- mark all external content and tool output as untrusted data
- prohibit untrusted data from overriding system/project/workflow rules
- search results cannot become executable code or canonical skill text without sandbox review
- critical physical parameters must cite paper text, official docs, or verified computation, not low-trust web snippets

### 20. Multi-Tool Chains Create Risks Not Visible In Single Tool Calls

Papers: `2502.09809` AgentGuard, ToolLLM, API-Bank, ToolEmu.

Current risk:

```text
Read private file -> summarize -> write public report -> upload/push is dangerous even if each individual operation looks benign.
```

Controls:

- add private-path taint tracking to artifacts
- enforce export whitelist before any public-facing write, upload, or commit
- define deny rules for dangerous tool sequences
- high-risk chains require dry-run or human gate

### 21. Emulated Or Simulated Safety Checks Can Be Over-Trusted

Papers: `2309.15817` ToolEmu, safety benchmark papers.

Current risk:

```text
An LLM-emulated sandbox or mocked tool check passes, but real COMSOL/Magnus/license/filesystem behavior differs.
```

Controls:

```text
emulated pass < dry-run pass < real sandbox pass < real execution pass
```

Reports must identify which level was achieved. Emulation can screen risk but cannot certify physical or operational success.

### 22. Scientific Workflow Can Solve The Wrong Problem Correctly

Papers: AI Scientist, AI-Researcher, Lang-PINN, Why LLMs Aren't Scientists Yet.

Current risk:

```text
The code runs and verifiers pass for the implemented model, but the implemented model is not the paper's physical problem.
```

Required new node before implementation:

```yaml
physics_formalization:
  outputs:
    geometry:
    materials:
    equations:
    boundary_conditions:
    sources:
    solver:
    observables:
    assumptions:
    missing_fields:
```

Code/COMSOL generation should consume this structured spec, not raw prose alone.

### 23. Dynamic Benchmarks Can Drift Just Like Skills

Papers: Benchmark Self-Evolving, SEAGym/PACE family.

Current risk:

```text
Automatically generated audit cases, parameter perturbations, and adversarial examples become part of replay without fixed labels, versions, or verifiers.
```

Controls:

- dynamic cases start as `candidate_benchmark`
- record generator prompt, source case, perturbation type, expected behavior, verifier, and human-confirmation status
- only verified benchmark cases enter replay/audit sets

### 24. Long-Horizon Partial Progress Can Be Misread As End-To-End Success

Papers: SWE-EVO, SWE-bench, coding-agent evaluations.

Current risk:

```text
A workflow improves one subgoal while regressing another, but the final report only records that some artifact was produced.
```

Controls:

- track subgoal gain/loss, not only final completion
- record `PASS->PASS`, `PASS->FAIL`, `FAIL->PASS`, and `FAIL->FAIL` transitions for replay cases
- canonical updates must report `fix_count`, `forget_count`, `cost_delta`, and safety-rule changes

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

Current `workflow_schema.yaml` contains only type, instruction, produces, next, branches, and retries. It does not encode risk level, stop conditions, skill loading, memory loading, verifier outputs, replay checks, provenance, uncertainty routing, template assumptions, or artifact-write policy.

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
provenance:
  required_artifacts: []
  answer_must_cite_artifact_ids: true
uncertainty:
  action_confidence: low | medium | high
  request_uncertainty: low | medium | high
  missing_fields: []
template_contract:
  slots: []
  fixed_assumptions: []
  does_not_apply_when: []
tool_chain_policy:
  taint_tracking: true
  export_whitelist_required: true
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

### Deficiency 6: No Provenance Manifest Strong Enough For Attribution

The expanded workflow/provenance and benchmark-audit papers show that pass/fail is not enough. A future reader must be able to tell whether a change helped because the workflow improved, the model changed, the loaded skill changed, the memory retrieval changed, the container changed, or the test got easier.

Required run-level records:

- workflow and case workflow hash
- AGENTS/project policy hash
- skill versions and loaded skill IDs
- memory IDs injected into each node
- model, inference parameters, and CLI/tool versions
- container/runtime digest
- artifact path, hash, producer node, and taint status
- human intervention points
- cost, retries, wall time, and failure taxonomy

### Deficiency 7: No Skill Integrity Or Supply-Chain Gate

Existing lifecycle fields are not enough if a skill package includes scripts, configs, examples, or resources. A skill may appear harmless in prose but execute broader actions through helper files.

Before promotion, every skill package needs:

- declared vs actual capability comparison
- private path / shell / network / write / credential access scan
- static check for executable snippets and hidden initialization behavior
- dry-run or sandbox behavior test for high-risk skills
- explicit permission and rollback policy

### Deficiency 8: No Uncertainty-To-Route Mechanism

The workflow still treats uncertainty mostly as supervisor judgment. It needs separate channels for action uncertainty and underspecification uncertainty.

If `request_uncertainty` is high, the correct route is usually `clarification` or `blocked`, not `debug`, `retry`, or `update_artifacts`.

### Deficiency 9: No Taint Tracking For Tool Chains And Export

Single-tool permissions are insufficient. The dangerous path is often a chain: read private artifact, summarize it, write a public report, then export or commit it.

Every artifact should carry at least:

```yaml
taint:
  private_source: true | false
  license_or_secret_adjacent: true | false
  public_export_allowed: true | false
  source_paths: []
```

### Deficiency 10: Mie Timeline Is Too Optimistic If It Also Serves As Benchmark Infrastructure

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

### Priority 6: Add Run Provenance And Artifact Identity

Do this before claiming any workflow improvement.

Minimum version:

- write one `run_manifest.yaml` per run
- assign stable IDs and hashes to generated artifacts
- record which node produced each artifact
- require provenance-based answers to cite artifact IDs
- return `unknown` when no log/artifact supports the claim

### Priority 7: Add Skill Integrity And Supply-Chain Checks

Before a skill can be promoted from candidate to active:

- compare declared and actual capabilities
- scan helper scripts/configs/examples/resources, not just `SKILL.md`
- block undeclared shell/network/private-path/canonical-write behavior
- require dry-run or sandbox test for privileged operations
- record permission scope and rollback handle

### Priority 8: Add Uncertainty Routing

Every planning/checking node should report at least:

```yaml
action_confidence:
request_uncertainty:
missing_fields: []
```

High request uncertainty should route to clarification/blocking. It must not be converted into more retries or self-modification.

### Priority 9: Add Taint Tracking And Tool-Chain Policies

Mark artifacts derived from private PDFs, private run folders, licenses, tokens, private logs, or secret-adjacent paths. Public export, GitHub operations, or long-term canonical writes must check the taint state.

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
9. Generated workflow topology is correct if the final report looks complete.
10. Multi-agent review is independent just because agents run in separate conversations.
11. A skill is safe if its markdown description looks safe.
12. Memory retrieval is beneficial if the retrieved item is semantically similar.
13. Benchmark pass rates mean improvement without full harness disclosure.
14. LLM-emulated or dry-run safety checks are equivalent to real sandbox execution.
15. A runnable physics script solves the paper's intended physical problem.

The papers largely argue against all fifteen assumptions.

## Final Recommendation

Keep the CLI-driven worker/supervisor architecture. Keep YAML workflow definitions. Keep the idea of self-iteration. But demote `update_artifacts` from “automatic self-improvement” to “evidence-gated governance”. Add verifiers, evidence logs, skill lifecycle states, replay tests, and paired acceptance gates before trusting any self-evolved workflow or skill.

Minimal actionable plan:

1. Update workflow schema with `risk_level`, `stop_conditions`, `human_review_conditions`, `verifiers`, `loads_skills`, `loads_memories`, `success_metrics`, `regression_checks`, `provenance`, `uncertainty`, `template_contract`, `tool_chain_policy`, and `artifact_write_policy`.
2. Replace direct `update_artifacts` writes with candidate patch generation.
3. Create attempt capsule and critic verdict files for every node execution.
4. Build Mie verifier suite first, before expanding to many papers.
5. Add active/candidate/deprecated lifecycle for lessons and skill items.
6. Add a small replay suite before any canonical workflow or skill update.
7. Add run manifests, artifact hashes, provenance-cited answers, skill integrity checks, and taint tracking.
8. Report all outcomes with the three-state distinction: pipeline, numerical job, physical reproduction.
