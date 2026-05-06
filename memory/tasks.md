# tasks.md — 任务追踪

> 由 Claw 维护。每次会话结束时更新。

---

## 进行中

_当前无进行中任务。_

## 待办

- [ ] 在 GitHub 新建「DailyFindings」仓库，将 `skills/DailyFindings/` 内容推送上去并启用 GitHub Actions

## 已完成

| 日期 | 任务 | 备注 |
|------|------|------|
| 2026-05-05 | 初始化 AI 工作空间 | 已创建 AGENTS.md、MEMORY.md、memory/ 目录结构 |
| 2026-05-05 | 将所有文件改为中文 | 响应主人要求，全面切换为中文 |
| 2026-05-05 | 日志结构重构 | 将单一 log.jsonl 改为按日期分文件存储（memory/logs/），最多保留30份 |
| 2026-05-05 | 开发「每日发现」skill | 完成 fetch_papers.py、daily_papers.yml、README.md，存放于 skills/每日发现/ |
| 2026-05-05 | 重构 skill 为 DailyFindings | 重命名为 DailyFindings，添加摘要概括功能，首页 README 每日自动更新（论文目录+概要+作者+机构），添加 index.json 历史索引，删除旧目录 skills/每日发现/ |
| 2026-05-06 | 编写 DailyFindings skill.md | 在 skills/DailyFindings/ 下创建详细可复用的 Agent 指令文档 |
