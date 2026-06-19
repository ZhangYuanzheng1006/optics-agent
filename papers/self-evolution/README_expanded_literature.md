# Expanded Self-Evolution / Agent Workflow Literature

This folder now covers more than the original `frameworks / failures / surveys` split. The goal is to support the `optics_agent` workflow-engine design: paper reproduction workflows, agent project groups, verifier gates, skill lifecycle governance, sandboxed runs, and batched self-iteration.

Current count after the expansion: **127 PDF files**.

## Search Coverage

Searches were expanded across these design-relevant areas:

- Agentic workflow generation and workflow optimization
- Multi-agent orchestration, coordinator/planner designs, and agent-to-agent failure modes
- Agent memory, lifelong learning, procedural memory, and experience distillation
- Agent skill architecture, skill libraries, skill drift, skill security, and skill evaluation
- Agent evaluation, benchmark methodology, verifier-driven systems, and uncertainty/clarification
- Tool-use agents and tool benchmarks
- Coding agents and long-horizon software-engineering agents
- Scientific discovery agents and autonomous research systems
- Planning/reasoning scaffolds for task decomposition
- Agent safety, sandboxing, red-teaming, memory poisoning, and tool-orchestration safety

## Categories

| Folder | Count | Why It Matters For This Project |
|---|---:|---|
| `agent_skills/` | 21 | Directly relevant to SKILL lifecycle, skill drift, skill validation, skill security, and self-maintaining skill libraries. |
| `workflow_optimization/` | 11 | Directly relevant to YAML workflow templates, case workflow generation, workflow performance prediction, and verifier-guided workflow search. |
| `multi_agent_orchestration/` | 14 | Supports the “agent project group” design: supervisor/PI, workers, independent reviewers, and domain experts. |
| `memory_lifelong/` | 12 | Supports memory lifecycle, experience consolidation, memory evaluation, and memory misevolution risks. |
| `evaluation_benchmarks/` | 7 | Supports success metrics, benchmark audit, uncertainty reporting, and verifier/evaluator design. |
| `safety_governance/` | 7 | Supports sandboxing, export whitelist, memory/tool poisoning defenses, and safety gates. |
| `scientific_agents/` | 6 | Supports research-workflow analogy and scientific reproduction pipeline design. |
| `tool_use/` | 6 | Supports tool interface design, tool benchmark design, and tool-call reliability. |
| `coding_agents/` | 5 | Supports long-horizon agent execution, patch verification, issue-solving workflows, and CLI-agent practices. |
| `planning_reasoning/` | 6 | Supports task decomposition, plan-execute-verify, graph/tree-of-thought style scaffolds. |
| `frameworks/` | 18 | Original successful or positive self-evolution/framework papers. |
| `failures/` | 10 | Original failure/collapse/safety-risk papers. |
| `surveys/` | 4 | Original broad surveys. |

## Suggested Reading Order

For current workflow-engine design, prioritize these papers first:

1. `workflow_optimization/2604.08224_Externalization_Memory_Skills_Protocols_Harness_Engineering.pdf`
2. `agent_skills/2602.12430_Agent_Skills_Architecture_Acquisition_Security_Path_Forward.pdf`
3. `workflow_optimization/2410.10762_AFlow_Automating_Agentic_Workflow_Generation.pdf`
4. `workflow_optimization/2410.07869_Benchmarking_Agentic_Workflow_Generation.pdf`
5. `workflow_optimization/2601.07477_JudgeFlow_Block_Judge_Workflow_Optimization.pdf`
6. `agent_skills/2605.13716_SkillOps_Self_Maintaining_Skill_Libraries.pdf`
7. `agent_skills/2605.10990_Skill_Drift_Is_Contract_Violation.pdf`
8. `agent_skills/2603.28815_SkillTester_Utility_and_Security_of_Agent_Skills.pdf`
9. `memory_lifelong/2604.15774_MemEvoBench_Memory_Misevolution_Safety.pdf`
10. `multi_agent_orchestration/2602.03128_MAFBench_Unified_Multi_Agent_Framework_Benchmark.pdf`
11. `workflow_optimization/2509.13978_LLM_Agents_Interactive_Workflow_Provenance.pdf`
12. `scientific_agents/2508.14111_Survey_Autonomous_Scientific_Discovery.pdf`
13. `safety_governance/2309.15817_ToolEmu_Sandboxed_Tool_Execution.pdf`
14. `safety_governance/2406.13352_AgentDojo_Dynamic_Environment_Attacks.pdf`
15. `evaluation_benchmarks/2605.21404_Pilot_Audit_LLM_Agent_Benchmark_Papers.pdf`

## Per-Folder Summaries

Each PDF-containing folder now has a Chinese `README_summaries.md` with one entry per paper. The summary format is consistent across subfolders: one-sentence conclusion, core contribution, workflow lessons, warnings, concrete design hooks for `optics_agent`, and priority.

- `agent_skills/README_summaries.md`
- `workflow_optimization/README_summaries.md`
- `multi_agent_orchestration/README_summaries.md`
- `memory_lifelong/README_summaries.md`
- `evaluation_benchmarks/README_summaries.md`
- `safety_governance/README_summaries.md`
- `scientific_agents/README_summaries.md`
- `tool_use/README_summaries.md`
- `coding_agents/README_summaries.md`
- `planning_reasoning/README_summaries.md`
- `frameworks/README_summaries.md`
- `failures/README_summaries.md`
- `surveys/README_summaries.md`

## Design Questions To Extract From Reading

When reading these papers, extract answers to these project-specific questions:

- How should `case_workflow.yaml` be generated, edited, verified, and replayed?
- What is the minimal schema for a workflow step, an expert-agent response, and an export bundle?
- How should skill items move through `candidate -> active -> deprecated`?
- How can skill drift and memory misevolution be detected before they affect canonical workflow assets?
- What should be measured for “workflow improved”: pass rate, cost, verifier score, replay regression, or human review score?
- Which agent failures are specific to multi-agent project groups: identity drift, echoing, coordination overhead, conflicting expert advice?
- What evidence is required before self-iteration modifies long-term assets?
- Which safety controls are needed for Docker/sandbox execution and export whitelist governance?

## Notes

- Some papers are duplicated across conceptual relevance in the broader bibliography, but each file is stored in one primary category here.
- `benchmarks/` is currently empty and can be removed or reused later for local benchmark definitions.
- Future reading notes should go under `notes/agent_skill_self_iteration/` or a new focused folder such as `notes/workflow_literature_review/`.
