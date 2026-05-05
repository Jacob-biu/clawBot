# MEMORY.md — 长期记忆

> 由 Claw 维护。每次会话结束后若有新上下文则更新。  
> 最后更新：2026-05-05

---

## 主人信息

- **GitHub：** Jacob-biu
- **仓库：** Jacob-biu/clawBot
- **交流语言：** 中文（简体）

## 偏好

- 喜欢直接、以行动为导向的回应
- 希望 AI 将重要信息写入文件，而非依赖对话上下文
- 重视轻量、不过度设计的方案
- 对长期 AI 工作空间概念（OpenClaw 风格）感兴趣
- **要求始终使用中文交流**

## 进行中的项目

| 项目 | 状态 | 备注 |
|------|------|------|
| AI 工作空间初始化 | ✅ 已完成 | 已创建 AGENTS.md、MEMORY.md、memory/ 目录结构 |
| 每日发现 skill | ✅ 已完成 | 见 skills/每日发现/，需部署到独立仓库「每日发现」 |

## 已开发的 Skills

| Skill 名称 | 路径 | 功能 | 状态 |
|-----------|------|------|------|
| 每日发现 | `skills/每日发现/` | 每天 UTC 00:00 拉取顶级 AI 机构的最新 Agent 论文，输出 Markdown 报告，并通过 GitHub Issue 通知所有者 | ✅ 开发完成，待部署 |

## 关键决策

- `AGENTS.md` 是核心操作文件，其他记忆文件为辅助
- 记忆目录使用 `tasks.md`（纯文本）+ `log.jsonl`（结构化日志）
- 不引入重型工具——纯 Markdown 与 JSONL 是主要格式

## Skills 部署说明

- **每日发现**：代码在 `skills/每日发现/`，需在 GitHub 上新建仓库「每日发现」，将该目录下所有文件（含 `.github/workflows/daily_papers.yml`）推送上去并启用 Actions。
  - 脚本仅使用 Python 标准库，零外部依赖
  - 机构列表在 `fetch_papers.py` 的 `TOP_INSTITUTIONS` 中维护

## 备注

_在此跨会话添加任何有用信息。_
