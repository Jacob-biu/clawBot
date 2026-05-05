#!/usr/bin/env python3
"""
每日 Agent 论文发现 — 核心脚本
从 arxiv 拉取最近24小时内发布的 Agent 相关顶级机构论文，
生成 Markdown 格式每日报告存入 daily/YYYY-MM-DD.md
"""

import os
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ═══════════════════════ 配置区域 ═══════════════════════

MAX_PAPERS = 20          # 每天最多输出论文数
FETCH_MAX   = 300        # 从 arxiv 拉取的最大候选数
HOURS_RANGE = 36         # 向前追溯小时数（略大于24h，以应对arxiv延迟）
OUTPUT_DIR  = Path("daily")

CATEGORIES = ["cs.AI", "cs.LG"]

# 顶级 AI 研究机构 / 大学关键词（大小写不敏感匹配）
TOP_INSTITUTIONS: list[str] = [
    # ── 科技公司 ──
    "Microsoft Research", "Microsoft",
    "Google DeepMind", "Google Brain", "Google Research", "Google",
    "DeepMind",
    "OpenAI",
    "Anthropic",
    "Meta AI", "Meta FAIR", "FAIR",
    "Amazon AWS", "Amazon",
    "Apple",
    "NVIDIA Research", "NVIDIA",
    "Samsung AI",
    "IBM Research",
    "Salesforce Research",
    "Adobe Research",
    "Baidu Research", "Baidu",
    "Alibaba DAMO", "Alibaba",
    "Tencent AI Lab", "Tencent",
    "Huawei Noah's Ark", "Huawei",
    "ByteDance Research", "ByteDance",
    "Meituan",
    # ── 北美顶级大学 ──
    "MIT", "Massachusetts Institute of Technology",
    "Stanford University", "Stanford",
    "Carnegie Mellon University", "CMU",
    "UC Berkeley", "University of California, Berkeley",
    "Harvard University", "Harvard",
    "Princeton University", "Princeton",
    "Yale University",
    "Columbia University",
    "University of Washington",
    "University of Michigan",
    "New York University", "NYU",
    "UCLA", "University of California, Los Angeles",
    "UCSD", "University of California, San Diego",
    "University of Illinois", "UIUC",
    "Cornell University", "Cornell",
    "Caltech", "California Institute of Technology",
    "Georgia Tech", "Georgia Institute of Technology",
    # ── 中国顶级大学 / 机构 ──
    "Tsinghua University", "Tsinghua",
    "Peking University", "PKU",
    "Zhejiang University", "ZJU",
    "Shanghai Jiao Tong University", "SJTU",
    "Fudan University",
    "University of Science and Technology of China", "USTC",
    "Renmin University",
    "Beihang University",
    "Harbin Institute of Technology", "HIT",
    "Nanjing University",
    "Chinese Academy of Sciences", "CAS",
    "Microsoft Research Asia", "MSRA",
    # ── 欧洲 / 其他 ──
    "University of Oxford", "Oxford",
    "University of Cambridge", "Cambridge",
    "ETH Zurich", "ETH Zürich", "ETHZ",
    "University of Toronto",
    "Mila", "Vector Institute",
    "INRIA",
    "Max Planck Institute",
    "National University of Singapore", "NUS",
    "Nanyang Technological University", "NTU",
    "Seoul National University", "SNU",
    "KAIST",
    "Allen Institute for AI", "AI2", "AllenAI",
    "Toyota Research Institute", "TRI",
    "JPMorgan AI Research",
]

# ═══════════════════════ arxiv 查询 ═══════════════════════

ARXIV_NS = {
    "atom":       "http://www.w3.org/2005/Atom",
    "arxiv":      "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}


def build_query() -> str:
    """构建 arxiv API 搜索查询字符串"""
    cat_q = " OR ".join(f"cat:{c}" for c in CATEGORIES)
    # 关键词同时匹配标题和摘要
    kw_pairs = [
        'ti:agent', 'abs:agent',
        'ti:"multi-agent"', 'abs:"multi-agent"',
        'ti:"LLM agent"', 'abs:"LLM agent"',
        'ti:"AI agent"', 'abs:"AI agent"',
        'ti:"agentic"', 'abs:"agentic"',
        'ti:"autonomous agent"', 'abs:"autonomous agent"',
        'ti:"tool use"', 'abs:"tool use"',
    ]
    kw_q = " OR ".join(kw_pairs)
    return f"({cat_q}) AND ({kw_q})"


def fetch_arxiv_papers(query: str, max_results: int = FETCH_MAX) -> list[dict]:
    """调用 arxiv API，返回解析后的论文列表"""
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": str(max_results),
        "start": "0",
    }
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    print(f"[INFO] 请求 arxiv API …")
    req = urllib.request.Request(url, headers={"User-Agent": "clawBot-DailyDiscovery/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        xml_bytes = resp.read()
    return _parse_atom(xml_bytes)


def _parse_atom(xml_bytes: bytes) -> list[dict]:
    """解析 arxiv Atom XML，提取论文字段"""
    root = ET.fromstring(xml_bytes)
    ns = ARXIV_NS
    papers: list[dict] = []

    for entry in root.findall("atom:entry", ns):
        p: dict = {}

        # 标题
        t = entry.find("atom:title", ns)
        p["title"] = (t.text or "").strip().replace("\n", " ") if t is not None else ""

        # arxiv URL (即 ID)
        id_el = entry.find("atom:id", ns)
        p["url"] = (id_el.text or "").strip() if id_el is not None else ""

        # 提交时间
        pub_el = entry.find("atom:published", ns)
        p["published"] = (pub_el.text or "").strip() if pub_el is not None else ""

        # 摘要
        sum_el = entry.find("atom:summary", ns)
        p["abstract"] = (sum_el.text or "").strip().replace("\n", " ") if sum_el is not None else ""

        # 作者 + 机构
        authors, affiliations = [], []
        for au in entry.findall("atom:author", ns):
            name_el = au.find("atom:name", ns)
            aff_el  = au.find("arxiv:affiliation", ns)
            if name_el is not None:
                authors.append((name_el.text or "").strip())
            if aff_el is not None and aff_el.text:
                aff = aff_el.text.strip()
                if aff and aff not in affiliations:
                    affiliations.append(aff)
        p["authors"]      = authors
        p["affiliations"] = affiliations

        # 分类标签
        cats = [c.get("term", "") for c in entry.findall("atom:category", ns)]
        p["categories"] = [c for c in cats if c]

        papers.append(p)

    return papers


# ═══════════════════════ 过滤逻辑 ═══════════════════════

def _within_hours(published: str, hours: int = HOURS_RANGE) -> bool:
    """判断论文是否在最近 `hours` 小时内发布"""
    try:
        pub_dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - pub_dt) <= timedelta(hours=hours)
    except Exception:
        return False


def _match_institution(paper: dict) -> tuple[bool, list[str]]:
    """
    检查论文是否来自顶级机构。
    优先检查 affiliations 字段，其次检查摘要全文（兜底策略）。
    返回 (是否匹配, 匹配到的机构名列表)。
    """
    aff_text  = " | ".join(paper.get("affiliations", []))
    # 仅在无 affiliation 信息时才回退到摘要搜索（避免误判）
    search_in = aff_text if aff_text else paper.get("abstract", "")

    matched: list[str] = []
    for inst in TOP_INSTITUTIONS:
        if inst.lower() in search_in.lower():
            if inst not in matched:
                matched.append(inst)

    return len(matched) > 0, matched


def filter_papers(papers: list[dict]) -> list[dict]:
    """过滤：最近24h（宽松36h）+ 顶级机构，最多 MAX_PAPERS 篇"""
    result: list[dict] = []
    seen_urls: set[str] = set()

    for p in papers:
        if p["url"] in seen_urls:
            continue
        if not _within_hours(p["published"]):
            break  # 已按时间降序排列，可提前终止
        matched, insts = _match_institution(p)
        if matched:
            p["matched_institutions"] = insts
            result.append(p)
            seen_urls.add(p["url"])
        if len(result) >= MAX_PAPERS:
            break

    return result


# ═══════════════════════ Markdown 生成 ═══════════════════════

def _fmt_paper(paper: dict, idx: int) -> str:
    """将单篇论文渲染为 Markdown 块"""
    title    = paper.get("title", "无标题")
    authors  = paper.get("authors", [])
    affs     = paper.get("affiliations", [])
    matched  = paper.get("matched_institutions", [])
    abstract = paper.get("abstract", "")
    url      = paper.get("url", "")
    pub      = paper.get("published", "")
    cats     = paper.get("categories", [])

    # 摘要截短
    if len(abstract) > 600:
        abstract = abstract[:600] + " …"

    authors_str = "、".join(authors[:6])
    if len(authors) > 6:
        authors_str += f" 等（共 {len(authors)} 位作者）"

    affs_str    = "；".join(affs) if affs else "（详见原文）"
    matched_str = "、".join(matched)
    cats_str    = " | ".join(cats[:3])

    return f"""### {idx}. {title}

| 字段 | 内容 |
|------|------|
| **作者** | {authors_str} |
| **作者机构** | {affs_str} |
| **顶级机构标签** | {matched_str} |
| **arxiv 分类** | {cats_str} |
| **发布时间** | {pub} |
| **原文链接** | [{url}]({url}) |

**摘要：**

> {abstract}

---
"""


def generate_markdown(papers: list[dict], date_str: str) -> str:
    """生成完整的每日论文 Markdown 报告"""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not papers:
        return (
            f"# 每日 Agent 论文发现 — {date_str}\n\n"
            f"> 今日（{date_str}）暂无符合条件的论文：最近36小时内、来自顶级机构、"
            f"Agent 相关。\n\n"
            f"*由 clawBot 每日发现 skill 自动生成 | {now_str}*\n"
        )

    header = (
        f"# 每日 Agent 论文发现 — {date_str}\n\n"
        f"> 自动筛选自 arxiv，来自顶级 AI 机构，发布于最近36小时内。  \n"
        f"> 关键词：agent、multi-agent、LLM agent、AI agent  \n"
        f"> **本次更新 {len(papers)} 篇论文**\n\n"
        f"---\n\n"
    )

    body   = "\n".join(_fmt_paper(p, i + 1) for i, p in enumerate(papers))
    footer = f"\n*由 clawBot 每日发现 skill 自动生成 | {now_str}*\n"

    return header + body + footer


# ═══════════════════════ 入口 ═══════════════════════

def main() -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[INFO] 开始拉取论文，日期：{today}")

    query = build_query()
    print(f"[INFO] 查询语句：{query[:120]} …")

    papers_raw = fetch_arxiv_papers(query)
    print(f"[INFO] 拉取候选论文：{len(papers_raw)} 篇")

    papers = filter_papers(papers_raw)
    print(f"[INFO] 筛选后符合条件：{len(papers)} 篇")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"{today}.md"
    out_file.write_text(generate_markdown(papers, today), encoding="utf-8")
    print(f"[INFO] 已写入 → {out_file}")

    # 将结果写入 GitHub Actions 环境变量
    gh_output = os.environ.get("GITHUB_OUTPUT", "")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"paper_count={len(papers)}\n")
            f.write(f"date={today}\n")

    return len(papers)


if __name__ == "__main__":
    sys.exit(0 if main() >= 0 else 1)
