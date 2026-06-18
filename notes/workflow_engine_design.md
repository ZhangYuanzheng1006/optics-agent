# 工作流引擎设计笔记

> 2026-06-18
> 本文档记录 optics_agent 工作流引擎的架构设计方案。

---

## 1. 核心概念

### 三个角色

```
用户运行: python workflow.py paper_reproduction.workflow.yaml
              │
              ▼
┌──────────────────────────────────────────────────┐
│               workflow.py (程序)                    │
│  读取 YAML 定义 → 管理 state → 通过 MCP 通信       │
│  不直接调用 agent，只提供数据和中继                   │
└──────────────────────┬───────────────────────────┘
                       │ MCP 通信
                       ▼
┌──────────────────────────────────────────────────┐
│            opencode (同一个对话)                    │
│                                                    │
│  ┌──────────────────────────────────────────┐     │
│  │        主管 agent (管理者)                │     │
│  │  • 接收 workflow 发来的节点配置和结果       │     │
│  │  • 按 YAML 的主管提示词做判断              │     │
│  │  • 给工作 agent 发当前任务的 prompt        │     │
│  │  • 维护主管经验笔记（防止忘掉踩过的坑）      │     │
│  │  • 通过 MCP 向 workflow 回传状态           │     │
│  └──────────────┬───────────────────────────┘     │
│                 │ 发送 prompt                      │
│  ┌──────────────▼───────────────────────────┐     │
│  │        工作 agent (执行者)                │     │
│  │  • 接收主管 agent 发来的当前任务 prompt    │     │
│  │  • 读取/操作文件                           │     │
│  │  • 运行 COMSOL、Magnus 等                  │     │
│  │  • 输出结果给主管 agent                    │     │
│  └──────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```

### 关键设计原则

- **工作流由 YAML 把握** — 拓扑、分支、节点 prompt 都在 YAML 中定义
- **主管和工作 agent 在同一对话** — 主管维持大局，工作 agent 只做当前任务
- **一次只发当前任务给工作 agent** — 避免上下文压缩丢失信息
- **主管 agent 不读 YAML** — workflow 程序通过 MCP 把节点信息推给主管
- **MCP 是双向通道** — workflow→主管（节点配置、工作结果），主管→workflow（进度、分支决策）
- **主管 agent 维持经验笔记** — 在对话中积累，防止长任务遗忘

## 2. 数据流

### 2.1 正常节点执行流程

```
workflow.py                             主管 agent                   工作 agent
    │                                      │                          │
    │  读取 YAML 下一节点定义                │                          │
    │                                      │                          │
    ├──MCP→ { 主管_prompt                  │                          │
    │         工作_prompt_choices           │                          │
    │         工作_agent_上次输出           │                          │
    │         MCP 工具 }                   │                          │
    │                                      │                          │
    │                                 主管读取主管_prompt              │
    │                                 主管判断选哪个工作_prompt        │
    │                                      │                          │
    │                                      ├──prompt→ (当前任务) ────→│
    │                                      │                          │ 执行
    │                                      │                          │ 读/写文件
    │                                      │←──output───────────────┤
    │                                      │                          │
    │                                 主管更新经验笔记                  │
    │                                 主管判断是否完成                  │
    │                                      │                          │
    │←──MCP─ {next, branch, fail} ─────────┤                          │
    │                                      │                          │
    │  更新 state → 下一节点                │                          │
```

### 2.2 分支节点流程

```
workflow.py                             主管 agent                   工作 agent
    │                                      │                          │
    │  到达 branch 节点                     │                          │
    ├──MCP→ { 主管_prompt(检查标准)         │                          │
    │         工作_agent_结果               │                          │
    │         分支选择: pass/fail           │                          │
    │         MCP 工具(branch_pass,         │                          │
    │                 branch_fail) }       │                          │
    │                                      │                          │
    │                                 主管读取工作 agent 的输出          │
    │                                 按 YAML 的检查标准评估            │
    │                                 （二重保险：独立判断+标准指导）    │
    │                                      │                          │
    │                                 如果复杂可启动子检查               │
    │                                 （总结上下文 → 新 agent 窗口）    │
    │                                      │                          │
    │←──MCP→ {branch: "pass", reason} ─────┤                          │
    │                                      │                          │
    │  检查 max_retries → 更新 state        │                          │
    │  路由下一节点                         │                          │
```

### 2.3 上下文丢失时的恢复流程

```
主管 agent 检测到工作 agent 输出不完整（上下文压缩）
    │
    主管 agent:
      "你的输出似乎被截断了，我重新发送任务。
       之前已完成：理论推导，当前需要你：生成 Java 代码。
       关键参数：波长 633nm，材料 Au+SiO2..."
    │
    重新发送给工作 agent（不含历史，只含当前必须的信息）
    │
    同时主管 agent 在自己的经验笔记中标注"此处曾发生上下文压缩"
```

### 2.4 开新 agent 窗口的流程（无上下文继承）

```
当需要无 bias 的独立检查时（如理论检查、数值检查）：
    │
    主管 agent 总结关键上下文（不含历史细节）:
      "需要检查的任务：theory_derivation
       预期结果：模式有效折射率应在 1.5-2.5 之间
       关键假设：TM 模式、弱引导"
    │
    传给新 agent 窗口（不含工作 agent 的历史）
    │
    新 agent 返回结果：
      {decision: "pass", reason: "..."}
    │
    主管 agent 继续
```

### 2.5 工作流自迭代流程（更新 YAML）

```
一轮复现结束后（或多次失败后）
    │
    主管 agent 总结:
      "本轮遇到的 prompt 不足：
       1. theory_derivation 的指导不够具体
       2. numerical_check 缺少对 neff=0 的检测
       工作流建议：
       在 theory_check 之前增加 material_check 节点"
    │
    传给专门的"工作流更新 agent"（加载了 workflow.yaml 语法 SKILL）
    │
    工作流更新 agent 修改 YAML 文件
    │
    主管 agent 确认修改
```

## 3. MCP 接口设计

### 3.1 workflow.py 暴露给主管 agent 的 MCP 工具

```
// 获取当前节点信息
tool get_current_node:
    返回: {node_id, type, description, 主管_prompt, 工作_prompt_choices, ...}

// 前进到下一节点
tool advance:
    参数: {next_node_id} 或 {branch: "pass"/"fail"}
    行为: 更新 state，进入下一节点
    返回: 下一节点信息

// 获取工作 agent 上次输出的文件内容
tool read_worker_output:
    参数: {file_path}
    返回: 文件内容

// 获取工作流历史摘要
tool get_workflow_summary:
    返回: {completed_nodes, current_node, retry_counts, 经验笔记}

// 更新主管经验笔记
tool update_experience:
    参数: {note: "..."}
    行为: 追加到 session 经验笔记

// 获取当前节点的工作 prompt（YAML 中配置的）
tool get_worker_prompt:
    参数: {choice_index}
    返回: prompt 文本

// 回退到上一节点
tool rollback:
    行为: current_node = previous_node，更新 state

// 重置工作流
tool reset_workflow:
    行为: 清空 state，从头开始

// 提交失败报告（超出 max_retries）
tool report_failure:
    参数: {node_id, reason, debug_log}
    行为: 生成 handoff 报告
```

### 3.2 主管 agent 的决策逻辑

```
收到 MCP 推送 → 读取:
  1. 主管_prompt（YAML 中该节点的"主管任务"）
  2. 工作 agent 的上次输出（或上次产物）
  3. YAML 中配置的工作_prompt_choices（给工作 agent 的 prompt 选项）
  4. 可用的 MCP 工具

主管 agent 的决策：
  1. 按主管_prompt 的指导理解当前应该做什么
  2. 评估工作 agent 的输出是否达标
  3. 选择合适的 prompt 发给工作 agent
  4. 或调用 MCP 工具前进/分支/回退
  5. 更新经验笔记

主管 agent 不做：
  ✗ 不直接读/写文件（那是工作 agent 的事）
  ✗ 不直接运行 COMSOL/Magnus
  ✗ 不解析 YAML 文件本身（workflow 通过 MCP 告诉它）
```

## 4. 节点定义（YAML 扩展）

每个节点需要包含：

```yaml
theory_derivation:
  type: prompt
  description: 推导理论模型

  # 主管 agent 的指导（workflow 通过 MCP 发送给主管）
  主管_prompt: |
    你的任务：检查工作 agent 是否已完成理论推导。
    判断标准：
    - 是否写出了控制方程？
    - 是否识别了边界条件？
    - 是否推导了预期物理行为？
    
    如果完成 → 调用 advance 进入下一节点。
    如果不足 → 将下面工作_prompt 发给工作 agent 继续工作。

  # 工作 agent 的 prompt 选项（主管选择其中一个发给工作 agent）
  工作_prompt:
    default: |
      基于论文参数，完成理论推导：
      1. 写出控制方程
      2. 确定边界条件
      3. 推导预期物理行为
      输出到 theory_derivation.md
    refine: |    # 可选：当上次推导不足时的补充指导
      补充推导：上次缺少边界条件分析。
      请补充：边界条件的数学形式、适用性分析。
  
  # 输入输出
  produces:
    - reproduction/private/<case>/theory_derivation.md
  consumes:
    - reproduction/private/<case>/params.yaml

  # 下一节点
  next: theory_check

---
theory_check:
  type: branch
  description: 检查理论推导

  主管_prompt: |
    你的任务：评估工作 agent 的理论推导质量。
    评估标准：
    - 方程量纲一致？(critical)
    - 边界条件合理？(critical)
    - 预期行为符合物理直觉？(normal)
    
    二重保险：不要只依赖工作 agent 的自我评价。
    用自己的判断做分支决策。
    
    决策：
    pass → 调用 MCP tool: advance {branch: "pass"}
    fail → 调用 MCP tool: advance {branch: "fail"}
    （YAML 重试限制：3 次）

  工作_prompt:
    default: |
      请自我检查理论推导的质量：
      - 方程量纲一致吗？
      - 边界条件合理吗？
      输出 pass/fail + 理由。
  
  branches:
    pass: numerical_program
    fail: theory_derivation
  max_retries: 3

---
update_artifacts:
  type: prompt
  description: 更新 SKILL 和工作流

  主管_prompt: |
    你的任务：基于本轮复现经验，更新项目工件。
    
    注意：这是高危操作，确保以下检查：
    1. SKILL 更新无格式错误
    2. 工作流修改合理
    
    更新完成后，将总结发给工作流更新 agent
    （加载了 workflow.yaml 语法 SKILL 的专门 agent）
    
    然后调用 advance。

  工作_prompt:
    analyze: |
      分析本轮复现，提取：
      - 新增的失败模式
      - 可复用的 Java API 技巧
      - prompt 不足之处
      输出到 analysis.md
    update_skill: |
      基于 analysis.md，更新对应的 SKILL.md
      追加 lessons learned
    update_workflow: |
      基于分析，修改 paper_reproduction.workflow.yaml
      - 递增 version
      - 追加 history
      - 调整拓扑（如需要）
  
  next: check_iteration
```

## 5. 主管经验笔记机制

```
主管 agent 在对话中维护一份"经验笔记"，随着工作流推进持续更新。

格式示例：

=== 主管经验笔记 ===
session: 2026-06-18_Degiron_Fig3

已完成节点:
1. paper_reading ✓  — 提取了参数，注意材料色散模型是 Drude
2. theory_derivation ✓ — 推导完成，关键假设是 TM 模式
3. numerical_program ✓ — Java 代码生成，使用了 ewfd 特征值求解

踩过的坑:
- mesh 默认太粗 → 需要显式设置 max_element_size = lambda/8
- 特征值 shift 初始值设为 1.5 导致矩阵分解失败 → 改为 2.0 后成功
- material 定义中 Au 的介电常数符号容易写反

当前状态:
- numerical_check 需要特别检查 neff 是否为零
- 如果 neff 为零 → 回 numerical_debug 调整 shift

待办:
- 更新 comsol-java-api SKILL 追加 ewfd shift 经验
===
```

## 6. 工作流 YAML 中单个节点的完整结构

```yaml
# 完整节点定义格式

node_id:
  type: prompt | branch | tool | parallel
  description: string
  
  # workflow 通过 MCP 发给主管 agent 的内容
  主管_prompt: string        # 主管当前节点的任务指导
  主管_prompt_file: string   # 或引用外部文件
  
  # 主管 agent 选择发给工作 agent 的 prompt
  工作_prompt:
    choice_name: string      # 每个选择是一个 prompt 文本
    choice_name_file: string # 或引用外部文件
    # 可以有多个 choice，主管根据情况选择
  
  # 节点输入输出
  consumes: [file_path]      # 工作 agent 需要的输入文件
  produces: [file_path]      # 工作 agent 应输出的文件
  
  # 节点转移（prompt 类型）
  next: node_id
  
  # 分支配置（branch 类型）
  branches:
    branch_name: next_node_id
  max_retries: 3
  
  # 是否需要开无上下文的新 agent
  new_agent: false           # true = 开新窗口（总结后传递）
```

## 7. workflow.py 程序结构

```python
# 顶层逻辑
def main(workflow_yaml_path):
    yaml = load_yaml(workflow_yaml_path)
    state = load_or_create_state()
    
    while state.current_node != "end":
        node = yaml.nodes[state.current_node]
        
        # 1. 通过 MCP 向主管 agent 推送节点信息
        mcp_send({
            "主管_prompt": node.主管_prompt,
            "工作_prompt_choices": node.工作_prompt.keys(),
            "worker_last_output": state.get_last_output(),
            "tools": ["advance", "rollback", "read_worker_output", ...]
        })
        
        # 2. 等待主管 agent 通过 MCP 调用工具
        action = mcp_wait_for_action()
        
        # 3. 处理主管的决策
        if action.type == "advance":
            if node.type == "branch":
                validate_branch(action.branch)
                check_retries(action.branch)
            state.advance(action.next_node)
        
        elif action.type == "rollback":
            state.rollback()
        
        elif action.type == "read_worker_output":
            mcp_response(read_file(action.file_path))
        
        # ... 其他工具
        
        state.save()
```

## 8. 与当前项目的关系

```
workflows/
├── paper_reproduction.workflow.yaml   # YAML 拓扑定义
├── ENGINE.md                          # 引擎指南
├── schemas/                           # 格式标准
├── prompts/                           # 可选：外部 prompt 文件
└── state/                             # 执行状态

SKILL 系统:
  optics-paper-reproduction SKILL 中增加:
    "当使用工作流模式时，由 workflow engine 驱动执行。
     主管 agent 和 工作 agent 在同一对话中协作。"
```

## 9. 后续讨论点

- 主管 agent 的工作 prompt 选择逻辑：自动还是需要人工确认？
- 经验笔记的保存方式：对话内积累 vs 写入文件？
- 无上下文新 agent 的启动流程：谁来总结？总结到什么粒度？
- 工作流修改的审批流程：主管提议 → 修改 agent 执行 → 主管确认？
