# DailyFindings — 每日 Agent 论文自动发现

> clawBot 自动化 skill：每天北京时间 08:00 从 arxiv 拉取顶级 AI 机构的最新 Agent 相关论文，  
> 自动生成摘要概括，并将论文目录与概要同步更新到仓库首页 README。

---

## 功能简介

| 特性 | 说明 |
|------|------|
| 📡 数据来源 | arxiv API（cs.AI / cs.LG 分类） |
| 🏛️ 机构筛选 | 最近36小时内发布 + 作者所属顶级机构（70+ 机构） |
| 🔍 关键词 | agent / multi-agent / LLM agent / AI agent / agentic |
| 📝 摘要概括 | 自动提炼每篇论文的结构化摘要（无需 LLM） |
| 📄 每日上限 | 最多 20 篇 |
| 📁 输出文件 | `daily/YYYY-MM-DD.md`（详细报告）+ `README.md`（首页） |
| ⏰ 定时任务 | UTC 00:00（北京时间 08:00），GitHub Actions |
| 📬 通知方式 | 自动创建 GitHub Issue，@仓库所有者 |
| 💾 历史索引 | `index.json`，追踪每日论文数量，用于首页归档展示 |

---

## 部署步骤

### 1. 新建 GitHub 仓库

在 GitHub 上新建名为 **`DailyFindings`** 的公开仓库（推荐公开，便于外部访问论文摘要）。

### 2. 将本目录下的文件推送到新仓库

```bash
# 将文件复制到新仓库（假设已克隆到 ~/DailyFindings）
cp fetch_papers.py requirements.txt ~/DailyFindings/
mkdir -p ~/DailyFindings/.github/workflows
cp .github/workflows/daily_papers.yml ~/DailyFindings/.github/workflows/

cd ~/DailyFindings
git add .
git commit -m "🚀 初始化 DailyFindings"
git push origin main
```

### 3. 确认 GitHub Actions 已启用

进入新仓库 → **Actions** 选项卡 → 确认工作流 `DailyFindings — 每日 Agent 论文发现` 已启用。

### 4. 手动触发测试

进入 Actions → `DailyFindings — 每日 Agent 论文发现` → **Run workflow** → 验证：
- `daily/YYYY-MM-DD.md` 是否生成
- `README.md` 是否自动更新（含论文目录与概要）
- 是否收到 GitHub Issue 通知

---

## 目录结构（部署后）

```
DailyFindings/
├── fetch_papers.py              ← 核心脚本（爬取、筛选、概括、生成 README）
├── requirements.txt             ← Python 依赖（当前仅标准库）
├── README.md                    ← 仓库首页（每日自动更新，展示论文目录与概要）
├── index.json                   ← 历史索引（日期 → 论文数，自动维护）
├── daily/
│   ├── 2026-05-05.md            ← 每日详细报告（自动生成）
│   └── ...
└── .github/
    └── workflows/
        └── daily_papers.yml     ← GitHub Actions 定时任务
```

---

## 输出说明

### `README.md`（仓库首页，每日自动更新）

首页展示：
1. **项目介绍**：功能概述、机构覆盖、更新频率
2. **今日论文目录**：表格形式，包含标题（链接）、核心概要（100字以内）、来源机构、第一作者
3. **今日论文详情**：可折叠卡片，包含完整作者列表、所属机构、关键词、摘要概括
4. **历史归档**：最近30天的日期链接与论文数量
5. **机构覆盖范围**：70+ 顶级机构列表

### `daily/YYYY-MM-DD.md`（每日详细报告）

- 论文目录（带跳转锚点）
- 每篇论文的完整信息：通讯作者 / 全部作者 / 所属机构 / 分类 / 关键词 / 原文链接
- 摘要概括（结构化提炼）
- 原始英文摘要（可折叠展开）

---

## 摘要概括原理

脚本使用**纯规则提取**（无需 LLM，零成本）：

1. 取摘要的**前2句**（通常描述问题背景和核心方法）
2. 若总句数 ≥ 4，追加**最后1句**（通常是实验结论）
3. 限制概括长度不超过 450 字符

同时自动提取论文关键词（agent 类别、方法论标签等），展示在详情卡片中。

---

## 顶级机构覆盖范围

脚本内置超过 **70 个** 顶级 AI 机构关键词，涵盖：

- **科技公司：** Microsoft、Google DeepMind、OpenAI、Anthropic、Meta AI、NVIDIA、Baidu、Alibaba、ByteDance 等
- **北美顶级大学：** MIT、Stanford、CMU、UC Berkeley、Harvard、Princeton、Cornell、Caltech 等
- **中国顶级大学/机构：** 清华大学、北京大学、浙大、上交大、复旦、中科院、MSRA 等
- **欧洲/其他：** Oxford、Cambridge、ETH Zurich、Mila、NUS、KAIST 等

如需扩充机构列表，直接编辑 `fetch_papers.py` 中的 `TOP_INSTITUTIONS` 列表即可。

---

## 本地测试

```bash
python fetch_papers.py
# 将在当前目录生成：
#   daily/YYYY-MM-DD.md  — 今日详细报告
#   README.md            — 更新后的首页
#   index.json           — 历史索引
```

---

*本 skill 由 [clawBot](https://github.com/Jacob-biu/clawBot)（Jacob-biu）自动开发和维护。*
