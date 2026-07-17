#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
curate_refs.py · raw JSON -> 큐레이션된 chN.bib (self-contained · stdlib only)
힘뇌장(HIMNOEJANG) 모노그래프 · 챕터 파이프라인 단계 ① 후반 (큐레이션)

수집된 raw 레코드를 저널 티어 점수 + 관련성 버킷 점수 + 배제 필터로
채점·선별하여 지정 개수(target)의 BibTeX 파일을 생성한다.
버킷·티어·쿼터·배제어는 --config JSON으로 주입한다(챕터별 조정).

의존: 없음 (Python 3.8+ 표준 라이브러리만)

config JSON 스키마(모든 키 선택 · 없으면 기본값):
{
  "target": 60,
  "header_title": "Chapter 12 · L-글루타민 (L-Glutamine)",
  "header_scope": "인지·장벽·GABA/글루타메이트·장뇌축 · 2013-2026",
  "tiers": {"nature": 9, "nutrients": 6, ...},          # 저널명 부분문자열 -> 점수
  "buckets": {"cognition": ["cognit","memory",...], ...}, # 버킷 -> 키워드 리스트
  "quotas": [["cognition", 14], ["mood", 10], ...],       # 버킷별 최소 확보
  "core_buckets": ["cognition","mood","gutbrain"],        # 있으면 가점, 없으면 감점
  "exclude_hard": ["kinase", ...],                         # -30
  "exclude_soft": ["genome", ...],                         # -8
  "title_gate": ["glutamine"]                              # (선택) 제목에 이 중 하나 필수
}

사용법:
  python scripts/curate_refs.py --raw references/ch12_raw.json \
      --out references/ch12.bib --config config_ch12.json
"""
import json, re, sys, io, argparse
from collections import Counter

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
except Exception:
    pass


def jscore(journal, tiers):
    jl = (journal or "").lower()
    return max([v for k, v in tiers.items() if k in jl] or [0])


def buckets_of(title, ptypes, buckets):
    s = (title or "").lower() + " " + " ".join(ptypes).lower()
    return {b for b, kw in buckets.items() if any(k in s for k in kw)}


def esc(s):
    return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def bibkey(rec, used):
    f = re.sub(r"[^A-Za-z]", "", rec["authors"][0].split()[0]) if rec["authors"] else "Anon"
    base = f"{f or 'Anon'}{rec['year']}"
    k, n = base, 1
    while k in used:
        n += 1
        k = f"{base}{chr(96 + n)}"
    used.add(k)
    return k


def main():
    ap = argparse.ArgumentParser(description="힘뇌장 참고문헌 큐레이션")
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", required=True, help="버킷/티어/쿼터/배제 JSON")
    ap.add_argument("--target", type=int, default=None, help="config.target 덮어쓰기")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    tiers = {k.lower(): v for k, v in cfg.get("tiers", {}).items()}
    buckets = cfg.get("buckets", {})
    quotas = cfg.get("quotas", [])
    core = set(cfg.get("core_buckets", list(buckets.keys())))
    ex_hard = [e.lower() for e in cfg.get("exclude_hard", [])]
    ex_soft = [e.lower() for e in cfg.get("exclude_soft", [])]
    title_gate = [g.lower() for g in cfg.get("title_gate", [])]
    target = args.target or cfg.get("target", 60)

    recs = json.load(open(args.raw, encoding="utf-8"))
    seen, uniq = set(), []
    for r in recs:
        if r["pmid"] not in seen:
            seen.add(r["pmid"]); uniq.append(r)
    recs = uniq

    scored = []
    for r in recs:
        tl = (r["title"] or "").lower()
        b = buckets_of(r["title"], r["ptypes"], buckets)
        js = jscore(r["journal"], tiers)
        s = js + 2 * len(b)
        pt = " ".join(r["ptypes"]).lower()
        if title_gate and not any(re.search(r"\b" + re.escape(g) + r"\b", tl) for g in title_gate):
            r["_s"] = -100; r["_b"] = sorted(b); scored.append(r); continue
        if any(e in tl for e in ex_hard):
            s -= 30
        if any(e in tl for e in ex_soft):
            s -= 8
        if "randomized controlled trial" in pt: s += 6
        if "meta-analysis" in pt: s += 5
        if "systematic review" in pt: s += 4
        if "review" in pt: s += 2
        if "clinical trial" in pt: s += 3
        if b & core: s += 3
        if not b: s -= 6
        r["_s"] = s; r["_b"] = sorted(b); scored.append(r)

    scored.sort(key=lambda r: r["_s"], reverse=True)
    chosen, ids = [], set()

    def add(r):
        if r["pmid"] not in ids and r["_s"] > 0:
            chosen.append(r); ids.add(r["pmid"]); return True
        return False

    for bk, q in quotas:
        c = 0
        for r in scored:
            if c >= q: break
            if bk in r["_b"]:
                if r["pmid"] not in ids and add(r): c += 1
                elif r["pmid"] in ids: c += 1
    for r in scored:
        if len(chosen) >= target: break
        add(r)
    chosen = chosen[:target]

    bc = Counter()
    for r in chosen:
        for b in r["_b"]: bc[b] += 1
    print(f"selected {len(chosen)}", file=sys.stderr)
    print("buckets:", dict(bc), file=sys.stderr)
    print("years:", dict(sorted(Counter(r['year'] for r in chosen).items())), file=sys.stderr)
    jc = Counter(r["journal"] for r in chosen)
    print(f"journals: {len(jc)}", file=sys.stderr)
    for j, n in jc.most_common(12):
        print(f"  {n:2d} {j}", file=sys.stderr)
    print("--- titles ---", file=sys.stderr)
    for r in sorted(chosen, key=lambda x: x['year']):
        print(f"  {r['year']} {r['title'][:78]}", file=sys.stderr)

    used, blocks = set(), []
    chosen.sort(key=lambda r: (r["year"], r["authors"][0] if r["authors"] else "z"))
    for r in chosen:
        k = bibkey(r, used)
        auth = " and ".join(r["authors"]) if r["authors"] else "Anonymous"
        e = [f"@article{{{k},", f"  author  = {{{esc(auth)}}},",
             f"  title   = {{{esc(r['title'])}}},", f"  journal = {{{esc(r['journal'])}}},",
             f"  year    = {{{r['year']}}},"]
        if r["volume"]: e.append(f"  volume  = {{{r['volume']}}},")
        if r["issue"]: e.append(f"  number  = {{{r['issue']}}},")
        if r["pages"]: e.append(f"  pages   = {{{r['pages']}}},")
        e += [f"  doi     = {{{r['doi']}}},", f"  pmid    = {{{r['pmid']}}},",
              f"  keywords = {{{','.join(r['_b'])}}},",
              f"  url     = {{https://doi.org/{r['doi']}}}", "}"]
        blocks.append("\n".join(e))

    title = cfg.get("header_title", "")
    scope = cfg.get("header_scope", "")
    header = (f"% {args.out}\n% {title} · Pre-research bibliography\n"
              f"% Source: PubMed E-utilities (NCBI)\n% Scope: {scope}\n"
              f"% Real PMID+DOI per entry. DOI<->title verification = Step 3.\n"
              f"% Total entries: {len(chosen)}\n\n")
    open(args.out, "w", encoding="utf-8").write(header + "\n\n".join(blocks) + "\n")
    print(f"\nWROTE {args.out} ({len(chosen)})", file=sys.stderr)


if __name__ == "__main__":
    main()
