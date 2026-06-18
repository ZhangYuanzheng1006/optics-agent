# 工作流引擎设计笔记

> 2026-06-18
> 本文档记录 optics_agent 工作流引擎的架构设计方案。

---

## 0. 为什么用 CLI 而非裸 API

Agent CLI（如 opencode）本质是一个**命令行控制的 vibe-coding IDE**：

- 通过 CLI 控制，workflow 程序可以启动/继续/结束对话
- agent 可以使用原生工具：读文件、写文件、运行 PowerShell、git 操作等
- optics_agent 的任务天然需要这些能力（读论文、写 Java、提 Magnus 作业、解析结果）
- 如果接入裸 API，agent 只是一个 LLM，无法直接操作文件系统和运行命令
- **CLI = LLM + 工具链 + 文件系统访问**，这才是完整的 coding agent

所以 workflow 程序通过 CLI 控制 agent，而不是直接调 API。

---

## 1. 数据流方向（核心）

```
workflow ──CLI──→ agent          # 程序启动/继续对话，发送完整 prompt
agent ────MCP──→ workflow        # agent 调用 MCP 工具控制工作流（前进/分支/回退）
agent ──回复文──→ workflow       # agent 的常规 AI 回复作为执行结果
```

### 一次节点执行的完整循环

```
workflow.py:
  1. 读取 YAML 当前节点定义
  2. 将各部分合成一段完整 prompt
     = 主管_prompt + 工作_prompt + 上次结果 + 可选说明
  3. 通过 CLI 发给 agent 对话（新开或继续同一对话）
     例如: opencode --prompt "..."

agent 对话:
  4. 收到完整 prompt
  5. 主管 agent 和工作 agent 在同一对话中按 prompt 工作
  6. 工作 agent 执行任务（读/写文件等）
  7. 主管 agent 做判断
  8. 如需前进/分支/回退 → 调用 MCP 工具通知 workflow
  9. AI 回复作为执行结果

workflow.py:
  10. 收到 MCP 指令（如 advance / branch pass）
  11. 更新 state.yaml
  12. 进入下一节点 → 回到步骤 1
```

### 一句话总结

```
workflow 通过 CLI 发 prompt 给 agent
agent 通过 MCP 调 workflow 的命令
agent 的回复是 workflow 读的结果
```

## 2. 程序架构

```
┌─────────────────────────────────────────────────┐
│              workflow.py (MCP Server)            │
│                                                   │
│  角色: 读 YAML → 管理 state → 构造 prompt         │
│        → 通过 CLI 发给 agent                      │
│        → 监听 MCP 请求（来自 agent）              │
│        → 更新 state → 下一循环                     │
│                                                   │
│  MCP tools exposed:                               │
│    advance(branch?)      # 前进到下一节点          │
│    rollback()            # 回退到上一节点          │
│    get_state()           # 查看当前进展           │
│    report_failure(msg)   # 报告失败               │
│                                                   │
│  启动方式:                                        │
│    python workflow.py paper_reproduction.workflow  │
└────────────────────┬────────────────────────────┘
                     │ CLI: opencode --prompt "..."
                     ▼
┌─────────────────────────────────────────────────┐
│              opencode (MCP Client)               │
│                                                   │
│  收到 prompt → 主管+工作 agent 协作               │
│  执行任务 → 调用 MCP 工具控制流程                  │
│  输出回复文本作为结果                               │
└─────────────────────────────────────────────────┘
```

## 3. 节点执行的完整细节

### 步骤 1: workflow 构造 prompt

```python
# workflow.py 内部逻辑
def build_prompt(node, state):
    return f"""
[工作流: paper_reproduction v{state.version}]
[当前节点: {node.id}]
[已完成: {state.completed_nodes}]

--- 主管任务 ---
{node.主管_prompt}
（你需要在此节点结束时，通过 MCP 工具决定下一步）

--- 工作任务 ---
{node.工作_prompt.default}

--- 上次结果 ---
{state.get_last_output()}

--- 可用 MCP 工具 ---
- advance(branch="pass") / advance(branch="fail") — 前进到下一节点
- rollback() — 回退到上一节点
- get_state() — 查看当前进展
- report_failure(reason) — 报告失败
"""
```

### 步骤 2: workflow 通过 CLI 发给 agent

```python
# 新对话
subprocess.run(["opencode", "--prompt", prompt_text])

# 或继续同一对话（如 opencode 支持 session 恢复）
subprocess.run(["opencode", "--session", session_id, "--prompt", prompt_text])
```

### 步骤 3: agent 收到 prompt 后工作

```
主管 agent 和工作 agent 在同一对话中:

主管 agent:
  读 "主管任务" → 知道当前要做什么判断
  等待工作 agent 执行 → 读工作结果
  评估 → 调 MCP 工具: advance(branch="pass")

工作 agent:
  读 "工作任务" → 知道当前要执行什么
  读/写文件、运行命令
  输出结果

两个 agent 都在同一个 AI 回复中完成工作。
```

### 步骤 4: agent 回复 + MCP 调用

```
Agent 的回复文本:
"已完成理论推导。
推导了 TM 模式的波动方程，边界条件设置为 PML。
输出文件: theory_derivation.md"

同时 agent 调用 MCP:
  advance(branch=None)  # 普通前进，无分支
```

### 步骤 5: workflow 处理

```
workflow.py 收到 MCP advance 调用:
  1. 更新 state.yaml
     completed_nodes 追加当前节点
     current_node = 下一节点
  2. 读取 agent 回复文本（存为节点结果）
  3. 循环到步骤 1，进入下一节点
```

## 4. 分支节点的细节

### 分支节点流程

```
workflow 构造分支节点的 prompt:
  "主管任务: 检查理论推导质量，做出 pass/fail 决策
   工作任务: 无（不需要工作 agent）
   评估标准: 方程量纲一致？边界条件合理？..."

agent 回复:
  "评估结果: 方程量纲正确，边界条件合理。
   结论: pass"

agent 调用 MCP:
  advance(branch="pass")
```

### 重试机制

```python
# workflow.py 内部
def handle_branch(node, state):
    branch = mcp_request.branch
    state.retry_counts[node.id] += 1
    
    if branch in node.branches:
        if state.retry_counts[node.id] > node.max_retries:
            return report_failure(f"{node.id} 超过重试上限")
        state.current_node = node.branches[branch]
    else:
        # 分支名不合法，让 agent 重试
        send_prompt(f"分支 '{branch}' 不在选项中，请从 {node.branches.keys()} 中选择")
```

## 5. 新 agent 窗口（无上下文继承）

```
当需要独立检查且不希望上下文 bias 时:

workflow 在节点定义中标记:
  theory_check:
    new_session: true   # 开新对话，无历史
    ```

workflow 构造 prompt:
  - 不含之前的对话历史
  - 只含当前节点需要的上下文（文件内容摘要）
  - 发给全新的 opencode 进程

新 agent 执行 → 返回结果 → 进程退出
workflow 继续原对话

主管 agent 如何参与:
  方案 A: workflow 让主管 agent 先总结关键上下文 → 传给新 agent
  方案 B: workflow 自己从 state 中提取关键信息 → 构造 prompt
```

## 6. workflow.py 程序结构

```python
class WorkflowEngine:
    def __init__(self, yaml_path):
        self.yaml = load_yaml(yaml_path)
        self.state = load_state()
        self.mcp = MCPServer(self)  # 暴露 MCP tools

    def run(self):
        while self.state.current_node != "end":
            node = self.get_current_node()
            
            # 1. 构造 prompt
            prompt = self.build_prompt(node)
            
            # 2. 通过 CLI 发给 agent
            output = self.send_to_agent(prompt, new_session=node.new_session)
            
            # 3. 等待 agent 回复 + MCP 调用
            result = self.wait_for_completion()
            # result = {mcp_action: ..., text_output: ...}
            
            # 4. 处理 MCP action
            self.handle_action(result.mcp_action, node)
            
            # 5. 保存 state
            self.state.save()

    def build_prompt(self, node):
        parts = [
            f"[工作流: {self.yaml.name} v{self.state.version}]",
            f"[当前节点: {node.id}]",
            f"[已完成: {', '.join(self.state.completed_nodes)}]",
            "",
            "--- 主管任务 ---",
            node.主管_prompt,
            "",
            "--- 工作任务 ---",
            node.工作_prompt.get("default", ""),
            "",
            "--- 上次结果 ---",
            self.state.get_last_output() if not node.new_session else "(新对话)",
            "",
            "--- 可用 MCP 工具 ---",
            "- advance(branch='pass'|'fail')",
            "- rollback()",
            "- get_state()",
        ]
        return "\n".join(parts)

    def send_to_agent(self, prompt, new_session=False):
        if new_session:
            # 新开对话
            return subprocess.run(["opencode", "--prompt", prompt], capture_output=True)
        else:
            # 继续当前对话（通过 session_id）
            return subprocess.run(["opencode", "--session", self.state.session_id, "--prompt", prompt], capture_output=True)

    def handle_action(self, action, node):
        if action.name == "advance":
            if node.type == "branch":
                branch = action.params.get("branch")
                if branch not in node.branches:
                    raise ValueError(f"无效分支: {branch}")
                self.state.retry_counts[node.id] += 1
                if self.state.retry_counts[node.id] > node.max_retries:
                    self.fail(f"{node.id} 超过重试上限")
                self.state.current_node = node.branches[branch]
            else:
                self.state.current_node = node.next
        elif action.name == "rollback":
            self.state.current_node = self.state.previous_node
        # ...

    def wait_for_completion(self):
        # 阻塞等待 agent 的 MCP 调用 + 回复完成
        # MCP 调用和回复文本是并行的
        return {
            "mcp_action": self.mcp.wait_for_action(),
            "text_output": self.mcp.wait_for_output()
        }
```

## 7. MCP 工具列表（agent → workflow）

| 工具 | 参数 | 说明 |
|------|------|------|
| `advance` | `branch: str` (可选) | 前进到下一节点。branch 节点时必须传分支名 |
| `rollback` | 无 | 回退到上一节点 |
| `get_state` | 无 | 返回当前 state 摘要 |
| `report_failure` | `reason: str` | 报告失败，生成 handoff 报告 |
| `read_file` | `path: str` | 读取工作 agent 产出的文件内容（供主管检查） |
| `get_node_info` | 无 | 获取当前节点完整定义 |
| `update_experience` | `note: str` | 追加到 session 经验笔记 |

## 8. YAML 节点定义示例

```yaml
theory_derivation:
  type: prompt
  description: 推导理论模型
  
  主管_prompt: |
    让工作 agent 完成理论推导。完成后检查：
    - 是否写出控制方程
    - 是否明确边界条件
    - 是否预测物理行为
    完成 → 调 advance()

  工作_prompt:
    default: |
      基于 params.yaml，完成理论推导：
      1. 写出控制方程
      2. 确定边界条件
      3. 分析预期物理行为
      输出: theory_derivation.md

  produces:
    - theory_derivation.md
  next: theory_check

---
theory_check:
  type: branch
  description: 检查理论推导质量
  
  主管_prompt: |
    检查 theory_derivation.md 的质量：
    - 方程量纲一致？(critical)
    - 边界条件合理？(critical)
    - 预期行为符合物理？(normal)
    决策 → advance(branch="pass"/"fail")
    
    二重保险：不要只依赖工作 agent 自我评价。
    用你自己的分析判断。
  
  工作_prompt:
    default: (无，此节点不需要工作 agent 执行)
  
  max_retries: 3
  branches:
    pass: numerical_program
    fail: theory_derivation
```

## 9. 当前笔记中待确认的问题

- **CLI 命令格式**：opencode 是否支持 `--prompt` 和 `--session` 参数？还是需要其他方式？
- **MCP 实现方式**：opencode 如何连接到 workflow.py 的 MCP server？通过配置文件？
- **新对话继续**：如何让 workflow 继续一个已有的 opencode 对话而非每次新建？
- **经验笔记持久化**：主管 agent 在对话中维护的经验笔记，在 `new_session=true` 时如何继承？
