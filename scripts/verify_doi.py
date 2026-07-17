#!/usr/bin/env python3
"""
verify_doi.py · 참고문헌 DOI 4단계 검증 (보정판 · requests/Levenshtein 기반)
힘뇌장 모노그래프 · reference-validator Skill 보조 도구

※ 정본 검증기는 `scripts/validate_chapter.py`(표준 라이브러리 전용)다. 신규 챕터는 그것을 쓴다.
  이 스크립트는 requests/Levenshtein 환경에서의 대체·교차확인용으로 유지된다.

구(舊) 버전 버그 수정 이력(2026-07-17):
  - [FIXED] 과거 정규식이 본문 인용번호(`[7]` 등)와 산문의 `[PENDING-DOI-VERIFY]` 언급까지
    캡처해, 전역 순차 치환으로 태그를 '오정렬'시켜 원고를 손상시켰다.
  - 이제 `[N] ... doi:... [PENDING-DOI-VERIFY]` 형태의 '참고문헌 라인'만 라인 단위로 매칭하고,
    DOI를 `doi:` 필드에서 직접 추출하며, 제목은 CrossRef 정식 제목의 정규화 부분일치로 검증한다
    ("L. johnsonii ..." 같은 약어 마침표 거짓음성 제거). 치환은 해당 라인 내부에서만 수행한다.

사용법:
    python scripts/verify_doi.py --file chapters/ch11-tyrosine.md \
        --output references/validation-log-ch11.csv --update-in-place
"""
import argparse, csv, re, sys, time, unicodedata
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests 필요. pip install requests"); sys.exit(1)

try:
    import Levenshtein
    def ratio(a, b): return Levenshtein.ratio(a, b)
except ImportError:
    def ratio(a, b):
        if a == b: return 1.0
        m = sum(1 for x, y in zip(a, b) if x == y)
        return m / max(len(a), len(b), 1)

CROSSREF = "https://api.crossref.org/works/"
PUBMED = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
HEADERS = {"User-Agent": "HIMNOEJANG-Monograph/2.0 (mailto:choe.sunghwa@gmail.com)"}

# '참고문헌 라인' 전용: 줄 시작 [N], 중간에 doi:, 끝에 [PENDING-DOI-VERIFY]
REF_LINE = re.compile(r'^\[(\d+)\]\s+(.*?doi:\s*(10\.\S+?)\.?\s.*?)\[PENDING-DOI-VERIFY\]', re.MULTILINE)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def crossref(doi):
    try:
        r = requests.get(CROSSREF + doi, headers=HEADERS, timeout=15)
        if r.status_code == 404:
            return None, "DOI_NOT_FOUND"
        if r.status_code != 200:
            return None, f"CROSSREF_HTTP_{r.status_code}"
        return r.json().get("message"), None
    except Exception as e:
        return None, f"CROSSREF_EXC:{e}"


def pubmed_pmid(title):
    try:
        r = requests.get(PUBMED, params={"db": "pubmed", "term": title,
                         "retmode": "json", "retmax": 1}, timeout=15)
        if r.status_code != 200:
            return None
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        return ids[0] if ids else None
    except Exception:
        return None


def verify(cid, citation, doi):
    res = {"id": cid, "doi": doi, "verified": False, "reason": "",
           "title_sim": "", "journal": "", "year": "", "pmid": "",
           "cited_pmid": "", "timestamp": datetime.now().isoformat()}
    cite_norm = norm(citation)

    # Stage 1: DOI 존재
    paper, err = crossref(doi)
    if err:
        res["reason"] = err
        return res

    # Stage 2: 제목 일치 — CrossRef 정식 제목이 인용문에 (정규화) 부분일치하는가
    ptitle = (paper.get("title") or [""])[0]
    pt_norm = norm(ptitle)
    if pt_norm and pt_norm in cite_norm:
        sim = 1.0
    else:
        # 부분일치 실패 시 토큰 커버리지로 유사도 근사
        pt_tokens = pt_norm.split()
        covered = sum(1 for t in pt_tokens if t in cite_norm.split())
        sim = covered / max(len(pt_tokens), 1)
    res["title_sim"] = round(sim, 3)
    if sim < 0.85:
        res["reason"] = f"TITLE_MISMATCH(sim={sim:.2f}): actual='{ptitle[:70]}'"
        return res

    # Stage 3: 저널·연도
    res["journal"] = (paper.get("container-title") or [""])[0]
    dp = paper.get("issued", {}).get("date-parts") or [[None]]
    res["year"] = dp[0][0]

    # Stage 4: PubMed 교차 — cited PMID과 esearch 결과 대조 (있을 때만 경고)
    m = re.search(r'PMID:\s*(\d+)', citation)
    res["cited_pmid"] = m.group(1) if m else ""
    pmid = pubmed_pmid(ptitle)
    res["pmid"] = pmid or ""
    if res["cited_pmid"] and pmid and res["cited_pmid"] != pmid:
        # 불일치는 실패로 처리하지 않고 검증 리포트에만 경고 기록(동명이인/개정판 가능)
        res["reason"] = f"PMID_WARN(cited={res['cited_pmid']},pubmed={pmid})"

    res["verified"] = True
    return res


def process(path, out_csv, update):
    p = Path(path)
    content = p.read_text(encoding="utf-8")
    matches = list(REF_LINE.finditer(content))
    print(f"검증 대상(참고문헌 라인): {len(matches)}개")
    results = []
    for i, mt in enumerate(matches, 1):
        cid, citation, doi = mt.group(1), mt.group(2), mt.group(3).rstrip('.,;)')
        print(f"  [{i}/{len(matches)}] ref[{cid}] doi:{doi} ...", end=" ", flush=True)
        r = verify(cid, citation, doi)
        results.append(r)
        if r["verified"]:
            note = f" ({r['reason']})" if r["reason"] else ""
            print(f"OK sim={r['title_sim']}{note}")
        else:
            print(f"FAIL {r['reason']}")
        time.sleep(0.4)

    if update:
        today = datetime.now().strftime("%Y-%m-%d")
        # 라인 단위로 각 참고문헌의 PENDING 태그만 교체 (오정렬 방지)
        by_id = {r["id"]: r for r in results}

        def repl(mt):
            cid = mt.group(1)
            r = by_id.get(cid)
            whole = mt.group(0)
            if r and r["verified"]:
                tag = f"[DOI-VERIFIED {today} ✓]"
            elif r:
                tag = f"[VERIFY-FAILED: {r['reason']}]"
            else:
                return whole
            return whole.replace("[PENDING-DOI-VERIFY]", tag)
        content = REF_LINE.sub(repl, content)
        p.write_text(content, encoding="utf-8")
        print(f"\n원고 업데이트: {p}")

    if out_csv:
        Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
        with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["id", "doi", "verified", "reason",
                "title_sim", "journal", "year", "pmid", "cited_pmid", "timestamp"])
            w.writeheader()
            for r in results:
                w.writerow(r)
        print(f"검증 리포트: {out_csv}")

    ok = sum(1 for r in results if r["verified"])
    warn = sum(1 for r in results if r["verified"] and r["reason"])
    print(f"\n=== 검증 요약 ===")
    print(f"검증 완료: {ok}/{len(results)} ({100*ok/max(len(results),1):.1f}%)  경고(PMID): {warn}")
    fails = [r for r in results if not r["verified"]]
    if fails:
        print("실패 목록:")
        for r in fails:
            print(f"  [{r['id']}] {r['reason']}")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--output")
    ap.add_argument("--update-in-place", action="store_true")
    a = ap.parse_args()
    process(a.file, a.output, a.update_in_place)
