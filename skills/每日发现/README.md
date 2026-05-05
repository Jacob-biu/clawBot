# 每日发现 · Daily Discovery

> clawBot 的第一个自动化 skill：每天北京时间 08:00 自动拉取并推送顶级 AI 机构的最新 Agent 相关论文。

---

## 功能简介

| 特性 | 说明 |
|------|------|
| 数据来源 | arxiv API（cs.AI / cs.LG 分类） |
| 筛选条件 | 最近36小时内发布 + 作者所属顶级机构 |
| 关键词 | agent / multi-agent / LLM agent / AI agent / agentic |
| 每日上限 | 最多 20 篇 |
| 输出格式 | Markdown → `daily/YYYY-MM-DD.md` |
| 定时任务 | UTC 00:00（北京时间 08:00），GitHub Actions |
| 通知方式 | 自动创建 GitHub Issue，@仓库所有者 |

---

## 部署步骤

### 1. 新建 GitHub 仓库

在 GitHub 上新建名为 **`每日发现`** 的公开仓库（或私有仓库均可）。

### 2. 将本目录下的文件推送到新仓库

```bash
# 复制文件到新仓库（假设新仓库已克隆到 ~/每日发现）
cp fetch_papers.py ~/每日发现/
cp requirements.txt ~/每日发现/
mkdir -p ~/每日发现/.github/workflows
cp .github/workflows/daily_papers.yml ~/每日发现/.github/workflows/

# 进入新仓库并推送
cd ~/每日发现
git add .
git commit -m "🚀 初始化每日发现 skill"
git push origin main
```

### 3. 确认 GitHub Actions 已启用

进入新仓库 → **Actions** 选项卡 → 确认工作流已启用。

### 4. 手动触发测试

进入 Actions → `每日 Agent 论文发现` → **Run workflow** → 验证功能是否正常。

---

## 目录结构（部署后）

```
每日发现/
├── fetch_papers.py              ← 核心爬取 & 筛选脚本
├── requirements.txt             ← Python 依赖（当前仅标准库）
├── README.md                    ← 本文件
├── daily/
│   ├── 2026-05-05.md            ← 每日论文报告（自动生成）
│   └── ...
└── .github/
    └── workflows/
        └── daily_papers.yml     ← GitHub Actions 定时任务
```

---

## 顶级机构覆盖范围

脚本内置超过 **70 个** 顶级 AI 机构关键词，涵盖：

- **科技公司：** Microsoft、Google DeepMind、OpenAI、Anthropic、Meta AI、NVIDIA、Baidu、Alibaba、ByteDance 等
- **北美顶级大学：** MIT、Stanford、CMU、UC Berkeley、Harvard、Princeton、Cornell、Caltech 等
- **中国顶级大学/机构：** 清华、北大、浙大、上交大、复旦、中科院、MSRA 等
- **欧洲/其他：** Oxford、Cambridge、ETH Zurich、Mila、NUS、KAIST 等

如需扩充机构列表，直接编辑 `fetch_papers.py` 中的 `TOP_INSTITUTIONS` 列表即可。

---

## 本地测试

```bash
python fetch_papers.py
# 将在当前目录创建 daily/YYYY-MM-DD.md
```

---

*本 skill 由 clawBot（Jacob-biu/clawBot）自动开发和维护。*
