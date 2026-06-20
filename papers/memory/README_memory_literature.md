# Vector Memory & Agent Evolution Literature

> 2026-06-20
> 34 PDFs covering vector memory systems, agent memory evolution, retrieval strategies, memory security, and benchmarks.

## Categories

| Folder | Count | Focus |
|---|---:|---|
| `memory_architectures/` | 8 | Memory consolidation, forgetting, sleep-Consolidated, biological-inspired decay, episodic/semantic/procedural separation, governing evolving memory |
| `self_evolving_memory/` | 12 | Self-evolving agents with experience memory, skill memory, reasoning memory, co-evolutionary capability expansion, decentralized memory |
| `memory_retrieval/` | 8 | Graph memory, active reconstruction, tool-augmented retrieval, cost-sensitive store routing, ranked retrieval, episodic reasoning |
| `memory_security/` | 2 | Zombie agents (persistent memory injection), membership inference attacks on agent memory |
| `memory_benchmarks/` | 4 | Long-context memory benchmark, very long-term conversational memory, self-evolving memory benchmark, procedural memory retrieval benchmark |

## Per-Folder Summaries

Each folder has a `README_summaries.md` with per-paper analysis formatted as:
- One-sentence conclusion
- Core method/contribution
- Lessons for our vector memory system
- Warnings/risks
- Concrete design hooks for `optics_agent`
- Priority (high/medium/low)

- `memory_architectures/README_summaries.md`
- `memory_benchmarks/README_summaries.md`
- `self_evolving_memory/README_summaries.md`
- `memory_retrieval/README_summaries.md`
- `memory_security/README_summaries.md`

## Key Papers by Priority

### Must-read for our design
1. `2603.11768` Governing Evolving Memory — risks of evolving memory, governance mechanisms
2. `2601.18642` FadeMem — biologically-inspired forgetting with differential decay
3. `2604.20943` SCM — sleep-consolidated memory with NREM/REM phases, algorithmic forgetting
4. `2605.16045` RecMem — recurrence-based consolidation, 87% token cost reduction
5. `2602.15654` Zombie Agents — persistent memory injection across sessions
6. `2606.06036` MRAgent — memory is reconstructed not retrieved, active graph
7. `2603.15658` Cost-Sensitive Store Routing — selective retrieval from multiple stores
8. `2605.18421` EvoMemBench — benchmarking agent memory from self-evolving perspective
9. `2602.02474` MemSkill — learnable and evolvable memory skills
10. `2510.08002` MUSE — hierarchical experience memory, Read-Write-Assess-Govern lifecycle

## Design Questions

These papers should answer:
1. Should our "no governance, pure retrieval" strategy survive, or do we need periodic consolidation?
2. Is pure vector + reranker enough, or do we need graph memory / active reconstruction?
3. How to prevent zombie agent attacks in our memory write pipeline?
4. What memory types (episodic/semantic/procedural) should our vector store distinguish?
5. Should memory skills (extraction/consolidation/pruning routines) be learnable and evolvable?
6. What can we borrow from biological forgetting (decay rates, sleep consolidation)?
7. Is decentralized memory relevant to our multi-agent project team design?
