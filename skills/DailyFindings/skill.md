# DailyFindings — Agent 技能指令文档

> **版本：** v1.0  
> **维护者：** clawBot（Jacob-biu）  
> **用途：** 供 AI Agent 直接参照，在目标仓库中从零生成可运行的 DailyFindings 功能。

---

## 一、技能概述

**DailyFindings** 是一个完全自动化的每日论文发现系统，功能如下：

- 每天北京时间 **08:00**（UTC 00:00）通过 GitHub Actions 定时触发
- 调用 **arxiv API** 拉取最近 36 小时内发布的 `cs.AI` / `cs.LG` 分类论文
- 通过 **关键词筛选**（agent / multi-agent / LLM agent / agentic）+ **顶级机构匹配**（70+ 机构）过滤候选论文，每日最多输出 20 篇
- 对每篇论文使用 **规则提取 + MyMemory 免费翻译 API** 生成中文摘要概括，**无需任何付费 LLM**
- 将结果写入三个文件：`daily/YYYY-MM-DD.md`（详细报告）、`README.md`（首页）、`index.json`（历史索引）
- 自动提交推送，并通过 **GitHub Issue** 通知仓库所有者
- 全程**零外部依赖**，仅使用 Python 标准库（`urllib`、`xml`、`re`、`json`、`datetime`、`pathlib`）

---

## 二、Agent 执行目标

当 Agent 收到"部署 DailyFindings"任务时，必须在目标仓库中完成以下工作：

1. 创建核心脚本 `fetch_papers.py`
2. 创建依赖声明文件 `requirements.txt`
3. 创建 GitHub Actions 工作流 `.github/workflows/daily_papers.yml`
4. 确保 `daily/` 目录存在（可通过创建 `.gitkeep` 占位）
5. 创建初始 `README.md`（首次运行后会被自动覆盖）
6. 创建初始 `index.json`（内容为空数组 `[]`）
7. 提交所有文件，推送到仓库 `main` 分支
8. 在 Actions 页面手动触发一次工作流，验证输出

---

## 三、目录结构（部署后）

```
DailyFindings/
├── fetch_papers.py              ← 核心脚本（爬取、筛选、摘要、生成文件）
├── requirements.txt             ← 依赖声明（当前仅标准库）
├── README.md                    ← 首页（每日自动覆盖更新）
├── index.json                   ← 历史索引（每日自动追加，保留最近60天）
├── daily/
│   ├── .gitkeep                 ← 初始占位文件
│   └── YYYY-MM-DD.md            ← 每日详细报告（自动生成）
└── .github/
    └── workflows/
        └── daily_papers.yml     ← GitHub Actions 定时任务
```

---

## 四、文件规范

### 4.1 `requirements.txt`

内容固定如下，无需修改：

```
# requirements.txt — DailyFindings skill 依赖
# 脚本目前仅使用 Python 标准库（urllib, xml, re, json, datetime, pathlib, os, sys）
# 此文件留空，供未来扩展使用

# 若需要更强大的 HTTP 客户端，可解除下行注释：
# requests>=2.31.0
```

---

### 4.2 `fetch_papers.py` — 核心脚本规范

脚本按以下模块顺序组织，Agent 须严格遵循：

#### 4.2.1 文件头与导入

```python
#!/usr/bin/env python3
"""
DailyFindings — 每日 Agent 论文发现核心脚本
从 arxiv 拉取最近36小时内发布的 Agent 相关顶级机构论文，
为每篇论文生成结构化摘要概括，
输出：
  daily/YYYY-MM-DD.md  — 当日详细报告
  README.md            — 仓库首页，展示最新论文目录与概要
"""

import os
import re
import sys
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
```

#### 4.2.2 配置区域（顶部常量）

| 常量 | 默认值 | 说明 |
|------|--------|------|
| `MAX_PAPERS` | `20` | 每天最多输出论文数 |
| `FETCH_MAX` | `300` | 从 arxiv 拉取的最大候选数 |
| `HOURS_RANGE` | `36` | 向前追溯小时数（略大于24h，应对 arxiv 处理延迟） |
| `OUTPUT_DIR` | `Path("daily")` | 每日报告输出目录 |
| `README_PATH` | `Path("README.md")` | 首页路径 |
| `INDEX_PATH` | `Path("index.json")` | 历史索引路径 |
| `CATEGORIES` | `["cs.AI", "cs.LG"]` | arxiv 分类 |

#### 4.2.3 `TOP_INSTITUTIONS` 列表

机构列表须包含以下所有机构（大小写不敏感匹配），分组如下：

**科技公司：**
```
Microsoft Research, Microsoft,
Google DeepMind, Google Brain, Google Research, Google,
DeepMind, OpenAI, Anthropic,
Meta AI, Meta FAIR, FAIR,
Amazon AWS, Amazon, Apple,
NVIDIA Research, NVIDIA,
Samsung AI, IBM Research,
Salesforce Research, Adobe Research,
Baidu Research, Baidu,
Alibaba DAMO, Alibaba,
Tencent AI Lab, Tencent,
Huawei Noah's Ark, Huawei,
ByteDance Research, ByteDance,
Meituan
```

**北美顶级大学：**
```
MIT, Massachusetts Institute of Technology,
Stanford University, Stanford,
Carnegie Mellon University, CMU,
UC Berkeley, University of California, Berkeley,
Harvard University, Harvard,
Princeton University, Princeton,
Yale University, Columbia University,
University of Washington, University of Michigan,
New York University, NYU,
UCLA, University of California, Los Angeles,
UCSD, University of California, San Diego,
University of Illinois, UIUC,
Cornell University, Cornell,
Caltech, California Institute of Technology,
Georgia Tech, Georgia Institute of Technology
```

**中国顶级大学/机构：**
```
Tsinghua University, Tsinghua,
Peking University, PKU,
Zhejiang University, ZJU,
Shanghai Jiao Tong University, SJTU,
Fudan University,
University of Science and Technology of China, USTC,
Renmin University, Beihang University,
Harbin Institute of Technology, HIT,
Nanjing University,
Chinese Academy of Sciences, CAS,
Microsoft Research Asia, MSRA
```

**欧洲/其他：**
```
University of Oxford, Oxford,
University of Cambridge, Cambridge,
ETH Zurich, ETH Zürich, ETHZ,
University of Toronto,
Mila, Vector Institute,
INRIA, Max Planck Institute,
National University of Singapore, NUS,
Nanyang Technological University, NTU,
Seoul National University, SNU,
KAIST,
Allen Institute for AI, AI2, AllenAI,
Toyota Research Institute, TRI,
JPMorgan AI Research
```

#### 4.2.4 arxiv API 模块

**函数：`build_query() -> str`**  
构建 arxiv API 搜索查询字符串。  
逻辑：`({cat_q}) AND ({kw_q})`，其中：
- `cat_q`：各分类以 `OR` 连接，格式 `cat:cs.AI OR cat:cs.LG`
- `kw_q`：关键词对以 `OR` 连接，包含：`ti:agent`, `abs:agent`, `ti:"multi-agent"`, `abs:"multi-agent"`, `ti:"LLM agent"`, `abs:"LLM agent"`, `ti:"AI agent"`, `abs:"AI agent"`

**函数：`fetch_arxiv_papers(query, max_results) -> list[dict]`**  
调用 `https://export.arxiv.org/api/query`，参数：`sortBy=submittedDate`，`sortOrder=descending`。  
User-Agent 设为 `clawBot-DailyFindings/1.0`，超时 90 秒。  
返回解析后的论文列表。

**函数：`_parse_atom(xml_bytes) -> list[dict]`**  
解析 arxiv Atom XML。每篇论文提取字段：
- `title`：规范化空白
- `url`：arxiv 论文 ID/链接
- `published`：格式 `YYYY-MM-DDTHH:MM:SSZ`
- `abstract`：规范化空白（`re.sub(r"\s+", " ", ...)`）
- `authors`：列表，每项为作者姓名
- `affiliations`：列表，去重，每项为机构字符串
- `categories`：列表，如 `["cs.AI", "cs.LG"]`

XML 命名空间：
```python
ARXIV_NS = {
    "atom":       "http://www.w3.org/2005/Atom",
    "arxiv":      "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}
```

#### 4.2.5 过滤模块

**函数：`_within_hours(published, hours) -> bool`**  
判断论文是否在最近 `hours` 小时内发布。  
格式解析：`datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)`。

**函数：`_match_institution(paper) -> tuple[bool, list[str]]`**  
若 `affiliations` 非空，在其中搜索；否则在 `abstract` 中搜索。  
大小写不敏感，返回 `(是否匹配, 已匹配机构列表)`。

**函数：`filter_papers(papers) -> list[dict]`**  
过滤逻辑：
1. URL 去重
2. 最近 36 小时内（`_within_hours`）— 不满足则 `break`（arxiv 结果按时间降序）
3. 顶级机构匹配（`_match_institution`）
4. 最多输出 `MAX_PAPERS` 篇

#### 4.2.6 摘要概括模块

**函数：`_split_sentences(text) -> list[str]`**  
按 `(?<=[.!?])\s+` 分割英文句子，过滤空项。

**函数：`_translate_to_zh(text, retries=2) -> str`**  
调用 MyMemory 免费翻译 API，无需 API Key：
- URL：`https://api.mymemory.translated.net/get`
- 参数：`q=<文本>&langpair=en|zh-CN&de=clawbot@noreply.github.com`
- 文本超过 450 字符时截断
- 解析响应 JSON，`responseStatus == 200` 时取 `responseData.translatedText`
- 失败重试 `retries` 次，全部失败时返回原英文附注"（翻译服务暂不可用）"
- 超时 15 秒

**函数：`summarize_paper(paper) -> str`**  
策略：
1. 取摘要前 2 句（背景/方法）
2. 若总句数 ≥ 4，追加最后 1 句（结论），且不与已选句重复
3. 调用 `_translate_to_zh` 翻译为中文

**函数：`extract_keywords(paper) -> list[str]`**  
在标题 + 摘要文本（小写）中匹配以下模式（按序，最多 5 个）：

| 模式 | 标签 |
|------|------|
| `multi-agent` | Multi-Agent |
| `llm agent` | LLM Agent |
| `ai agent` | AI Agent |
| `agentic` | Agentic |
| `reasoning` | Reasoning |
| `planning` | Planning |
| `reinforcement learning` | Reinforcement Learning |
| `rag` | RAG |
| `retrieval` | Retrieval |
| `benchmark` | Benchmark |
| `evaluation` | Evaluation |
| `code generation` | Code Generation |
| `chain-of-thought` | Chain-of-Thought |
| `fine-tuning` | Fine-tuning |
| `simulation` | Simulation |
| `embodied` | Embodied AI |
| `robotics` | Robotics |
| `web agent` | Web Agent |
| `memory` | Memory |
| `workflow` | Workflow |

#### 4.2.7 Markdown 生成 — 每日详细报告

**函数：`_fmt_paper_detail(paper, idx) -> str`**  
单篇论文 Markdown 块，格式：

```markdown
### {idx}. {title}

<table>
<tr><td><b>通讯作者</b></td><td>{前3作者} 等</td></tr>
<tr><td><b>全部作者</b></td><td>{前6作者}（共N位）</td></tr>
<tr><td><b>作者机构</b></td><td>{affiliations以；连接}</td></tr>
<tr><td><b>顶级机构标签</b></td><td>{matched_institutions前4个}</td></tr>
<tr><td><b>arxiv 分类</b></td><td>{categories前3个，| 分隔}</td></tr>
<tr><td><b>发布时间</b></td><td>{published}</td></tr>
<tr><td><b>关键词</b></td><td>`tag1` · `tag2` · ...</td></tr>
<tr><td><b>原文链接</b></td><td><a href="{url}">{url}</a></td></tr>
</table>

#### 📝 摘要概括

> {summary}

#### 📄 原始摘要（英文）

<details>
<summary>展开查看完整摘要</summary>

{abstract}

</details>

---
```

**函数：`generate_daily_markdown(papers, date_str) -> str`**  
无论 papers 是否为空均生成文件，空时输出友好提示。  
非空时结构：目录（带锚点链接）→ 论文详情（`_fmt_paper_detail`）→ 页脚。

**辅助函数：`_slugify(text) -> str`**  
生成 GitHub Markdown anchor：小写 → 去非字母数字字符 → 空白/下划线转连字符 → strip `-`。

#### 4.2.8 README 生成 — 仓库首页

**函数：`_load_index() -> list[dict]`**  
读取 `index.json`，失败时返回空列表。

**函数：`_save_index(index) -> None`**  
按 `date` 降序排序，**保留最近60条**，写回 `index.json`（`ensure_ascii=False`，`indent=2`）。

**函数：`generate_readme(papers, date_str) -> str`**  
生成仓库首页，结构：
1. **项目介绍**：标题、特性表格（数据来源、机构筛选、关键词、每日上限、更新时间、通知方式）
2. **今日论文**：若无论文输出提示；若有则：
   - 今日统计行：论文数 + 更新时间 + 完整报告链接
   - 论文概览表（6列）：`#` | 标题链接（≤60字符）| 核心概要（≤100字符）| 来源机构 | 第一作者
   - 论文详情：可折叠卡片（`<details><summary>` 标签），每张卡片包含：所属机构、全部作者、关键词、摘要概括
3. **历史归档**：从 `index.json` 加载，最近30天，表格展示日期链接 + 论文数
4. **机构覆盖范围**：列出所有 `TOP_INSTITUTIONS` 关键词
5. **页脚**：生成时间戳 + clawBot 链接

注意：Markdown 表格中的 `|` 字符须转为 `｜`（全角），换行符须替换为空格，以防表格错位。

#### 4.2.9 主流程 `main()`

```
main() 执行步骤：
1. 初始化目录：OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
2. 获取今日日期字符串：datetime.now(timezone.utc).strftime("%Y-%m-%d")
3. 构建 query → 拉取论文 → 过滤论文
4. 为每篇论文：
   a. summarize_paper(p) → p["summary"]
   b. extract_keywords(p) → p["keywords"]
5. 生成每日报告：OUTPUT_DIR / f"{date_str}.md"
6. 加载历史索引 → 追加/更新当日记录（{date, count}）→ 保存索引
7. 生成并写入 README.md
8. 设置 GitHub Actions 输出变量（用于工作流步骤间传值）：
   - 向 GITHUB_OUTPUT 写入：paper_count={count}
   - 向 GITHUB_OUTPUT 写入：date={date_str}
9. 打印摘要信息，正常退出
```

**错误处理：**
- 所有 HTTP 请求均有超时
- arxiv 请求失败时：打印错误信息，用空列表继续执行（不抛出），确保工作流不因网络抖动中断
- 翻译失败：降级为原英文 + 提示（见 4.2.6）

---

### 4.3 `.github/workflows/daily_papers.yml` — GitHub Actions 工作流规范

#### 触发条件

```yaml
on:
  schedule:
    - cron: '0 0 * * *'   # UTC 00:00 = 北京时间 08:00，每天自动运行
  workflow_dispatch:        # 支持手动触发（用于测试）
```

#### 顶层环境变量

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true   # 适配 Node24，避免弃用警告
```

#### 权限

```yaml
permissions:
  contents: write   # 允许提交并推送 daily/ 和 README.md
  issues: write     # 允许创建通知 Issue
```

#### 执行步骤（共7步）

**Step 1 — 检出仓库**
```yaml
- uses: actions/checkout@v4
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
```

**Step 2 — 配置 Python**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'
```

**Step 3 — 安装依赖**
```yaml
- run: |
    pip install --upgrade pip
    [ -f requirements.txt ] && pip install -r requirements.txt || true
```

**Step 4 — 执行脚本（id: fetch）**
```yaml
- id: fetch
  run: python fetch_papers.py
```

**Step 5 — 提交推送**  
逻辑：配置 git 用户 → `git add daily/ README.md index.json` → 若 `--cached` 无差异则跳过，否则提交并推送。  
提交信息格式：`📚 DailyFindings 更新：{date} — 共 {paper_count} 篇`，其中 `paper_count` 来自步骤 `fetch` 的 `outputs`（`${{ steps.fetch.outputs.paper_count }}`）。

**Step 6 — 确保 Label 存在**  
使用 `actions/github-script@v7`，检查名为 `DailyFindings` 的 Label 是否存在，若不存在则创建：
- `color: '0075ca'`
- `description: 'clawBot DailyFindings 每日论文自动通知'`

**Step 7 — 创建通知 Issue**  
使用 `actions/github-script@v7`，调用 `github.rest.issues.create`：
- `title`：`📚 DailyFindings 每日 Agent 论文推送 — {date}`
- `body`：@仓库所有者，含论文数、今日报告链接、README 链接；若 paper_count 为 0 则输出警告提示
- `labels`：`['DailyFindings']`

---

## 五、部署步骤（Agent 执行清单）

Agent 在执行部署任务时，按以下顺序操作：

```
[ ] 1. 确认目标仓库存在（若不存在，提示用户先在 GitHub 创建）
[ ] 2. 在仓库根目录创建 requirements.txt（内容见 §4.1）
[ ] 3. 在仓库根目录创建 fetch_papers.py（按 §4.2 规范实现）
[ ] 4. 创建 .github/workflows/ 目录
[ ] 5. 创建 .github/workflows/daily_papers.yml（按 §4.3 规范实现）
[ ] 6. 创建 daily/.gitkeep（确保 daily/ 目录被 git 追踪）
[ ] 7. 创建初始 index.json（内容：[]）
[ ] 8. 创建初始 README.md（可简单放置占位内容，首次运行后自动覆盖）
[ ] 9. 提交所有文件：git add . && git commit -m "🚀 初始化 DailyFindings"
[   ] 10. 推送到主分支
[ ] 11. 进入 GitHub Actions → 手动触发工作流 → 验证输出（见 §六）
```

---

## 六、验证方法

手动触发工作流后，验证以下结果：

| 检查项 | 预期结果 |
|--------|---------|
| `daily/YYYY-MM-DD.md` 存在 | ✅ 文件已生成，含论文目录和详情 |
| `README.md` 已更新 | ✅ 包含今日论文表格和历史归档 |
| `index.json` 已更新 | ✅ 包含今日日期和论文数条目 |
| GitHub Issue 已创建 | ✅ @Jacob-biu，标签 DailyFindings |
| 工作流运行状态 | ✅ 绿色（成功），无报错 |

若论文数为 0，说明当天 arxiv 无符合条件的论文，属正常情况（仍会生成空报告和 Issue 提示）。

---

## 七、自定义与扩展

| 需求 | 修改位置 | 说明 |
|------|---------|------|
| 添加机构 | `fetch_papers.py` → `TOP_INSTITUTIONS` | 追加机构关键词字符串 |
| 增加关键词 | `fetch_papers.py` → `build_query()` | 在 `kw_pairs` 中添加 `ti:"xxx"` 或 `abs:"xxx"` |
| 更改每日上限 | `fetch_papers.py` → `MAX_PAPERS` | 默认 20 |
| 更改追溯时间窗 | `fetch_papers.py` → `HOURS_RANGE` | 默认 36 小时 |
| 更改运行时间 | `daily_papers.yml` → `cron` | 默认 `0 0 * * *`（UTC 00:00） |
| 添加 arxiv 分类 | `fetch_papers.py` → `CATEGORIES` | 如 `cs.CL`、`cs.RO` |
| 扩展关键词标签 | `fetch_papers.py` → `extract_keywords()` → `kw_map` | 添加新模式和标签 |

---

## 八、常见问题

**Q：工作流运行报错 `Permission denied` 推送失败？**  
A：检查仓库 Settings → Actions → General → Workflow permissions，确保设置为 "Read and write permissions"。

**Q：翻译 API 频繁失败？**  
A：MyMemory 免费版每天有请求配额限制。若论文数量较多，部分摘要可能回退为英文原文，属正常降级行为。可将 `de` 参数的邮箱替换为真实邮箱以提升配额。

**Q：arxiv API 拉取结果为空？**  
A：arxiv 在周末不发布新论文（周六/周日 UTC），此时 paper_count 为 0 属正常。

**Q：如何关闭 Issue 通知？**  
A：删除工作流中的 Step 6（确保标签存在）和 Step 7（创建通知 Issue）即可。

---

*本文档由 [clawBot](https://github.com/Jacob-biu/clawBot) 自动生成并维护。*
