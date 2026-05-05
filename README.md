# clawBot

用于 GitHub Copilot 长期使用的个人 AI 工作空间。

本仓库是 **clawBot** 的家——一个驻留式 AI 代理，能够跨会话维护记忆、追踪任务、持续做事。

## 快速开始（给 Copilot）

1. 读取 [`AGENTS.md`](./AGENTS.md) — 你的操作规范与身份定义。
2. 读取 [`MEMORY.md`](./MEMORY.md) — 当前长期上下文。
3. 查看 [`memory/tasks.md`](./memory/tasks.md) 确认进行中任务。
4. 执行工作，完成后按 `AGENTS.md` 中的收尾清单操作。

## 文件说明

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 核心操作规范（每次会话必读） |
| `MEMORY.md` | 长期记忆：偏好、项目、决策 |
| `memory/tasks.md` | 任务追踪：进行中 / 待办 / 已完成 |
| `memory/log.jsonl` | 结构化会话活动日志 |
